from pr.core.diff_parser import GitDiffParser
from pr.core.diff_semantics import DiffSemanticAnalyzer
from pr.core.change_classifier import ChangeClassifier
from pr.core.impact_analyzer import ImpactAnalyzer
from pr.core.issue_parser import IssueParser

from pr.explanation.change_writer import ChangeWriter
from pr.explanation.context_writer import ContextWriter
from pr.explanation.impact_writer import ImpactWriter

from pr.formatter.checklist_builder import ChecklistBuilder
from pr.formatter.markdown_builder import MarkdownBuilder


def generate_pr_markdown(
    *,
    diff_text: str,
    files: list[str],
    payload: dict,
    template: str,
) -> str:
    """
    High-level PR generation pipeline (OO-based).
    """

    # --- Parse diff ---
    parser = GitDiffParser()
    file_diffs = parser.parse(diff_text)

    # --- Semantic analysis ---
    semantic_analyzer = DiffSemanticAnalyzer()
    semantics = semantic_analyzer.analyze(file_diffs)

    # --- Classification ---
    classifier = ChangeClassifier()
    classification = classifier.classify(semantics, files)

    # --- Impact analysis ---
    impact_analyzer = ImpactAnalyzer()
    impact_stats = impact_analyzer.scope(semantics)
    risk = impact_analyzer.risk_level(impact_stats)

    # --- Issue extraction ---
    issue = IssueParser().parse(payload)

    # --- Writing sections ---
    change_section = ChangeWriter().write(semantics)
    context_section = ContextWriter().write(semantics, issue)
    impact_section = ImpactWriter().write(impact_stats)

    checklist = ChecklistBuilder().build(classification, risk)

    # --- Final markdown ---
    builder = MarkdownBuilder(template)
    return builder.build({
        "change": change_section,
        "context": context_section,
        "impact": impact_section,
        "checklist": checklist,
    })
