"""Input-validation errors shared by the core library and the server.

The checker rejects a submission before running any code when the student's
files do not fit the challenge workspace (ADR-0018 D18.4); the server turns
:class:`SandboxError` into a 422 with the same Russian message.
"""

from __future__ import annotations


class SandboxError(ValueError):
    """A project submission cannot run in the sandbox (message is for students)."""

    @property
    def message(self) -> str:
        return str(self.args[0]) if self.args else ""
