from __future__ import annotations

def decision(path_a_positive: bool, path_b_positive: bool) -> str:
    if path_a_positive and path_b_positive:
        return "priority"
    if path_a_positive:
        return "caution"
    if path_b_positive:
        return "monitor"
    return "ignore"
