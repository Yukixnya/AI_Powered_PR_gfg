from fastapi import FastAPI
from pydantic import BaseModel

from core.diff_parser import GitDiffParser
from core.diff_semantics import DiffSemanticAnalyzer
from core.issue_parser import IssueParser
from core.change_classifier import ChangeClassifier
from core.impact_analyzer import ImpactAnalyzer

from explanation.context_writer import ContextWriter
from explanation.change_writer import ChangeWriter
from explanation.impact_writer import ImpactWriter

from formatter.checklist_builder import ChecklistBuilder
from formatter.markdown_builder import MarkdownBuilder


import os

app = FastAPI(title="God-Level PR Writer")

# Load template
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "base.md")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()



class PRRequest(BaseModel):
    git_diff: str
    issue: str


class PRResponse(BaseModel):
    title: str
    summary: str



@app.post("/generate-pr", response_model=PRResponse)
def generate_pr(req: PRRequest):
    # -----------------------------
    # Core analysis
    # -----------------------------
    parsed_diff = GitDiffParser(req.git_diff).parse()
    first_file = next(iter(parsed_diff.keys())) if parsed_diff else "unknown"
    semantics = DiffSemanticAnalyzer(parsed_diff).analyze()

    issue = IssueParser(req.issue).parse()

    classifier = ChangeClassifier(issue, semantics)
    classification = classifier.classify()

    impact = ImpactAnalyzer(
        stats=next(iter(parsed_diff.values()))
        if parsed_diff else None
    )

    # -----------------------------
    # Explanation layers
    # -----------------------------
    context = ContextWriter(issue, classification).write()
    changes = ChangeWriter(semantics).write()
    impact_text = ImpactWriter(impact, classification).write()
    checklist = ChecklistBuilder(classification).build()

    # -----------------------------
    # Title generation
    # -----------------------------
    title_prefix = classification.change_type.title()

    if classification.change_type == "refactor":
        title = f"Refactor: formatting cleanup in {first_file}"
    elif classification.change_type == "bug fix":
        title = f"Fix: {issue.summary.lower()}"
    elif classification.change_type == "feature":
        title = f"Feature: {issue.summary}"
    else:
        title = f"{title_prefix}: update {first_file}"

    # -----------------------------
    # Markdown assembly (summary)
    # -----------------------------
    builder = MarkdownBuilder(template)

    summary_md = builder.build({
        "context": context,
        "changes": changes,
        "impact": impact_text,
        "checklist": checklist,
    })

    return PRResponse(
        title=title,
        summary=summary_md
    )


