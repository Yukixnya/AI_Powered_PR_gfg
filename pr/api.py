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
    parser = GitDiffParser(diff_text)
    file_diffs = parser.parse()

    # --- Semantic analysis ---
    semantic_analyzer = DiffSemanticAnalyzer(file_diffs)
    semantics = semantic_analyzer.analyze()

    # --- Classification ---
    classifier = ChangeClassifier()
    classification = classifier.classify(semantics, files)

    # --- Impact analysis ---
    impact_analyzer = ImpactAnalyzer(semantics)
    impact_stats = impact_analyzer.scope()
    risk = impact_analyzer.risk_level()

    # --- Issue extraction ---
    issue = IssueParser(payload).parse()

    # --- Writing sections ---
    change_section = ChangeWriter(semantics).write()
    context_section = ContextWriter(semantics, issue).write()
    impact_section = ImpactWriter(impact_stats).write()

    checklist = ChecklistBuilder(classification, risk).build()


    # --- Final markdown ---
    builder = MarkdownBuilder(template)
    return builder.build({
        "change": change_section,
        "context": context_section,
        "impact": impact_section,
        "checklist": checklist,
    })
