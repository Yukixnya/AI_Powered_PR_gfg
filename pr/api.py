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


app = FastAPI(title="God-Level PR Writer")


class PRRequest(BaseModel):
    git_diff: str
    issue: str


class PRResponse(BaseModel):
    pull_request: str


@app.post("/generate-pr", response_model=PRResponse)
def generate_pr(req: PRRequest):
    # -----------------------------
    # Core analysis
    # -----------------------------
    parsed_diff = GitDiffParser(req.git_diff).parse()
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
    # Title
    # -----------------------------
    title_prefix = classification.change_type.title()
    first_file = next(iter(parsed_diff.keys()), "core logic")
    title = f"{title_prefix}: update {first_file}"

    # -----------------------------
    # Markdown assembly
    # -----------------------------
    template = open("templates/base.md", encoding="utf-8").read()

    builder = MarkdownBuilder(template)

    pr_markdown = builder.build({
        "title": title,
        "context": context,
        "changes": changes,
        "impact": impact_text,
        "checklist": checklist,
    })

    return PRResponse(pull_request=pr_markdown)
