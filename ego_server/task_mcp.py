"""Shared task-authoring MCP; Forgejo OAuth identity, current Ego roles.

OAuth tokens are audience-bound reference tokens managed by FastMCP's
OAuthProxy. Upstream credentials remain in its encrypted persistent store.
Tools reuse the existing REST interface in-process, retaining all Task Studio
validation, content-root containment and optimistic concurrency checks.
"""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from urllib.parse import quote

import httpx
from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, OAuthProxy, TokenVerifier
from fastmcp.server.dependencies import get_access_token
from key_value.aio.stores.filetree import FileTreeStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

from ego_server.auth import create_token
from ego_server.config import settings
from ego_server.db import get_connection
from ego_server.forgejo import _base_url


def _mapped_user(issuer: str, subject: str) -> dict | None:
    """Use verified issuer/subject, never a provider username or client role."""
    db = get_connection()
    try:
        row = db.execute(
            "SELECT s.id,s.username,s.role FROM external_identities e "
            "JOIN students s ON s.id=e.user_id WHERE e.issuer=? AND e.subject=?",
            (issuer, subject),
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


class ForgejoVerifier(TokenVerifier):
    """Validate the upstream OAuth token through trusted TLS UserInfo."""

    def __init__(self, issuer: str, *, transport: httpx.AsyncBaseTransport | None = None):
        super().__init__(required_scopes=["openid", "profile"])
        self.issuer = _base_url(issuer)
        self.transport = transport

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or len(token) > 32767:
            return None
        try:
            async with httpx.AsyncClient(
                timeout=15, follow_redirects=False, trust_env=False, transport=self.transport
            ) as client:
                response = await client.get(
                    self.issuer + "/login/oauth/userinfo",
                    headers={"Authorization": "Bearer " + token},
                )
                response.raise_for_status()
                profile = response.json()
            subject = profile.get("sub") if isinstance(profile, dict) else None
            if (
                not isinstance(subject, str)
                or not subject
                or len(subject) > 255
                or not subject.isascii()
                or any(ord(c) < 33 or ord(c) > 126 for c in subject)
            ):
                return None
            user = _mapped_user(self.issuer, subject)
            if not user or user["role"] not in {"admin", "mentor"}:
                return None
            return AccessToken(
                token=token,
                client_id=settings.mcp_forgejo_client_id,
                scopes=["openid", "profile"],
                subject=subject,
                claims={"forgejo_issuer": self.issuer, "forgejo_subject": subject},
            )
        except (httpx.HTTPError, ValueError, TypeError):
            # Never return provider responses, tokens or request headers.
            return None


def current_author(*, write: bool = False) -> dict:
    token = get_access_token()
    if token is None:
        raise ToolError("OAuth authentication required")
    issuer = token.claims.get("forgejo_issuer")
    subject = token.claims.get("forgejo_subject")
    if issuer != _base_url(settings.forgejo_url) or not isinstance(subject, str):
        raise ToolError("Invalid MCP identity")
    user = _mapped_user(issuer, subject)
    roles = {"admin"} if write else {"mentor", "admin"}
    if not user or user["role"] not in roles:
        raise ToolError("Current Ego role does not permit this operation")
    return user


def create_task_mcp(api_app: FastAPI, *, auth: OAuthProxy | None = None) -> FastMCP:
    """Build tools; passing auth is useful for isolated transport tests."""
    if auth is None:
        base = _base_url(settings.public_url)
        issuer = _base_url(settings.forgejo_url)
        store_path = settings.mcp_storage_path
        store_path.mkdir(parents=True, exist_ok=True, mode=0o700)
        encryption_key = base64.urlsafe_b64encode(
            hashlib.sha256(b"cogito-mcp-store\0" + settings.mcp_signing_key.encode()).digest()
        )
        auth = OAuthProxy(
            upstream_authorization_endpoint=issuer + "/login/oauth/authorize",
            upstream_token_endpoint=issuer + "/login/oauth/access_token",
            upstream_client_id=settings.mcp_forgejo_client_id,
            upstream_client_secret=settings.mcp_forgejo_client_secret,
            token_verifier=ForgejoVerifier(issuer),
            base_url=base,
            redirect_path="/mcp-callback",
            forward_pkce=True,
            forward_resource=False,
            token_endpoint_auth_method="client_secret_post",
            require_authorization_consent=True,
            jwt_signing_key=settings.mcp_signing_key,
            fastmcp_access_token_expiry_seconds=3600,
            client_storage=FernetEncryptionWrapper(
                key_value=FileTreeStore(data_directory=store_path),
                fernet=Fernet(encryption_key),
            ),
        )
    server = FastMCP(
        "Cogito Tasks",
        auth=auth,
        instructions=(
            "Read cogito://task-authoring before editing. Read an existing task to obtain "
            "version and content_etag; propose and validate a complete candidate. "
            "save_task publishes immediately to canonical files and re-syncs Ego; use it "
            "only when the user asks to save/publish. A 409 requires reviewing concurrent "
            "changes, never silently retrying with a new etag. This version edits existing "
            "tasks; validation checks structure/syntax, not curriculum case execution."
        ),
    )

    async def call_api(method: str, path: str, *, body: dict | None = None, write=False):
        user = current_author(write=write)
        jwt_token = create_token(
            user_id=user["id"], username=user["username"], role=user["role"], expires_in_seconds=60
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=api_app),
            base_url="http://localhost",
            timeout=60,
            trust_env=False,
        ) as client:
            response = await client.request(
                method, path, json=body, headers={"Authorization": "Bearer " + jwt_token}
            )
        if response.status_code >= 400:
            data = response.json()
            raise ToolError(
                f"Ego HTTP {response.status_code}: {data.get('detail', 'request failed')}"
            )
        return response.json()

    read = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}

    @server.tool(annotations=read)
    def whoami() -> dict:
        """Current linked Ego account and role; roles are read fresh from Ego."""
        user = current_author()
        return {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "can_save_tasks": user["role"] == "admin",
        }

    @server.tool(annotations=read)
    async def get_catalog(query: str = "") -> dict:
        """Browse/search projects, folders and existing tasks in the current catalog."""
        suffix = "?q=" + quote(query, safe="") if query else ""
        return await call_api("GET", "/admin/catalog" + suffix)

    @server.tool(annotations=read)
    async def get_task(task_id: str) -> dict:
        """Read canonical markdown, reference and tests plus version/content_etag.

        Check writable/read_only_reason before editing. Use the catalog's `id`.
        """
        return await call_api("GET", f"/admin/tasks/{quote(task_id, safe='')}/studio")

    @server.tool(annotations=read)
    async def list_students() -> list[dict]:
        """List students with progress summaries, for authorized teachers only."""
        return await call_api("GET", "/admin/students")

    @server.tool(annotations=read)
    async def get_student_progress(student_id: str) -> list[dict]:
        """Read stored progress for a student; presence of files is not progress."""
        return await call_api("GET", "/progress/" + quote(student_id, safe=""))

    @server.tool(annotations=read)
    async def get_student_understanding(student_id: str) -> list[dict]:
        """Read checked-solution defense status and exact student evidence.

        Test success and understanding are separate. confirmed refers only to
        the particular solution/version; it is not a claim of global mastery.
        Does not expose provider keys, billing or the student's source snapshot.
        """
        return await call_api("GET", "/progress/" + quote(student_id, safe="") + "/understanding")

    @server.tool(annotations=read)
    async def validate_task(
        task_id: str,
        expected_version: str,
        expected_content_etag: str,
        markdown: str,
        solution_py: str,
        tests_py: str,
    ) -> dict:
        """Admin-only validation of a full proposed edit, without publishing.

        Checks parser, Python syntax, smoke-case presence, declared version and
        etag. Does NOT execute curriculum tests. Supply version/etag from get_task.
        """
        return await call_api(
            "POST",
            f"/admin/tasks/{quote(task_id, safe='')}/studio/validate",
            body={
                "expected_version": expected_version,
                "expected_content_etag": expected_content_etag,
                "markdown": markdown,
                "solution_py": solution_py,
                "tests_py": tests_py,
            },
            write=True,
        )

    @server.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        }
    )
    async def save_task(
        task_id: str,
        expected_version: str,
        expected_content_etag: str,
        markdown: str,
        solution_py: str,
        tests_py: str,
    ) -> dict:
        """PUBLISH an existing task edit immediately. Admin only.

        Replaces canonical files and synchronizes Ego DB. This is not a draft
        save and does not commit/push Git. Use only on the user's save/publish
        request. Review changes and validate first. Never bypass a stale etag.
        """
        return await call_api(
            "PUT",
            f"/admin/tasks/{quote(task_id, safe='')}/studio",
            body={
                "expected_version": expected_version,
                "expected_content_etag": expected_content_etag,
                "markdown": markdown,
                "solution_py": solution_py,
                "tests_py": tests_py,
            },
            write=True,
        )

    @server.resource("cogito://task-authoring")
    def authoring_guide() -> str:
        """Task format, versioning and the MCP publication workflow."""
        current_author()
        return Path(__file__).with_name("mcp_authoring.md").read_text(encoding="utf-8")

    return server
