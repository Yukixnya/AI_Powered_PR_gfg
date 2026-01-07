def diff_summary(diffs: str) -> str:
    added = 0
    removed = 0

    for line in diffs.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1

    return f"{added} lines added, {removed} lines removed"
