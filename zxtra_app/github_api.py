import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def fetch_pr_files(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_pr_body(owner: str, repo: str, pr_number: int, body: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    payload = {
        "body": body
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

