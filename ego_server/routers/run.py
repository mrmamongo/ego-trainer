"""Run router — POST /run: execute arbitrary Python in the sandbox (IDE Run).

Uses the same ego.runner sandbox as the checker (timeout, temp dir, no
network, blocked imports) — see ADR-0001 D12. Unlike /check this endpoint
does not require a task binding and does not record progress: it exists so
the in-browser IDE gets a "Run" button with stdout/stderr feedback.
"""

from __future__ import annotations

import contextlib

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from ego.runner import run_code
from ego_server.deps import CurrentUser
from ego_server.models import RunCodeRequest, RunCodeResponse
from ego_server.service_settings import load_settings

router = APIRouter()


@router.post("", response_model=RunCodeResponse)
async def run_student_code(body: RunCodeRequest, user: CurrentUser) -> RunCodeResponse:
    """Run Python code in the sandbox and return raw output."""
    conn = None
    try:
        from ego_server.db import get_connection

        conn = get_connection()
        config = load_settings(conn)
    finally:
        if conn is not None:
            with contextlib.suppress(Exception):
                conn.close()
    if len(body.code) > config.max_code_chars:
        raise HTTPException(
            status_code=413, detail="Code exceeds the configured size limit"
        )
    result = await run_in_threadpool(
        run_code, body.code, timeout=config.check_timeout_seconds
    )
    return RunCodeResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        timed_out=result.timed_out,
        blocked_import=result.blocked_import,
    )
