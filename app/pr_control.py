from pr.api import generate_pr_markdown


def pr_controller(payload: dict):

    owner = payload["owner"]
    repo = payload["repo"]
    git_diff_text = payload["diff"]
    files = payload.get("files", [])

    # pr_title = payload.get("pr_title", "Auto Generated PR")
    # base = payload.get("base", "main")
    # head = payload.get("head")

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
        diff_text=git_diff_text,
        files=files,
        payload={
            "owner": owner,
            "repo": repo,
        },
        template=template
    )

    # update_pr_body(owner, repo, pr_number, pr_content)

    return {
        "status": "success",
        "repo": f"{owner}/{repo}",
        "pr_content": pr_content,
    }

