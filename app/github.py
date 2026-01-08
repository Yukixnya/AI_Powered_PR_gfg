from app.github_api import fetch_pr_files, update_pr_body
from pr.api import generate_pr_markdown


def github_webhook(payload: dict):

    # GitHub ping event
    if payload.get("zen"):
        return {"status": "pong"}

    if payload.get("action") != "opened":
        return {"status": "ignored"}

    repo = payload["repository"]["name"]
    owner = payload["repository"]["owner"]["login"]
    pr_number = payload["pull_request"]["number"]

    pr_files = fetch_pr_files(owner, repo, pr_number)

    files = []
    diffs = ""

    for f in pr_files:
        files.append(f["filename"])
        if f.get("patch"):
            diffs += f["patch"] + "\n"

    template = """
## Summary
{{change}}

## Context
{{context}}

## Impact
{{impact}}

## Checklist
{{checklist}}
"""

    pr_content = generate_pr_markdown(
        diff_text=diffs,
        files=files,
        payload=payload,
        template=template
    )

    update_pr_body(owner, repo, pr_number, pr_content)

    return {
        "status": "updated",
        "message": "PR description updated successfully"
    }

