from app.github_api import fetch_pr_files , update_pr_body
from app.diff_parser import diff_summary
from app.classifier import change_classifier
from app.pr_writer import pr_generator


def github_webhook(payload: dict):

    # ✅ Handle GitHub ping
    if payload.get("zen"):
        return {"status": "pong"}

    # ✅ Only act on PR opened
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

    summary = diff_summary(diffs)
    classification = change_classifier(files, summary)

    pr_content = pr_generator(
        files=files,
        diff_summary=summary,
        pr_type=classification,
        issue=None
    )

    update_pr_body(owner, repo, pr_number, pr_content)

    return {
        "status": "generated",
        "pr_content": pr_content
    }
