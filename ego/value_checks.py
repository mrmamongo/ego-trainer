"""Pure data checks shared by the checker and its generated subprocess code.

These functions deliberately need no imports: runner embeds their source in
the sandbox, where the installed ego package is unavailable.
"""


def _ego_same_value(left, right):
    """Compare literal data, ignoring dict order but retaining scalar types."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return len(left) == len(right) and all(
            any(
                _ego_same_value(key, other_key) and _ego_same_value(value, other_value)
                for other_key, other_value in right.items()
            )
            for key, value in left.items()
        )
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(
            _ego_same_value(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, (set, frozenset)):
        return len(left) == len(right) and all(
            any(_ego_same_value(a, b) for b in right) for a in left
        )
    return left == right


def _ego_mutable_ids(value, seen=None):
    """Find mutable containers in literal data, including nested aliases."""
    if seen is None:
        seen = set()
    if id(value) in seen:
        return set()
    seen.add(id(value))
    found = {id(value)} if isinstance(value, (dict, list, set)) else set()
    if isinstance(value, dict):
        children = value.values()
    elif isinstance(value, (list, tuple, set, frozenset)):
        children = value
    else:
        children = ()
    for child in children:
        found.update(_ego_mutable_ids(child, seen))
    return found
