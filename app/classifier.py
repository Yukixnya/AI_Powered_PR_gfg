def change_classifier(files: list, summary: str) -> str:
    if not files:
        return "Chore"

    if any("test" in f.lower() for f in files):
        return "Test update"

    if any(f.endswith(".md") for f in files):
        return "Documentation update"

    return "Code change"
