"""Pure data checks shared by the checker and its generated subprocess code.

The implementations live in :mod:`ego.exec_helpers` (import-free, so the
sandbox wrapper can embed their source); they are re-exported here under
their historical names.
"""

from ego.exec_helpers import (  # noqa: F401 — re-export for compatibility
    _ego_mutable_ids,
    _ego_same_value,
)

__all__ = ["_ego_same_value", "_ego_mutable_ids"]
