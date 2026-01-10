from pr.core.diff_parser import GitDiffParser
from pr.core.diff_semantics import DiffSemanticAnalyzer
from pr.core.change_classifier import ChangeClassifier

from pr.core.impact_analyzer import ImpactAnalyzer, ImpactStats

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
    High-level PR generation pipeline.
    """

    # --- Parse diff ---
    parser = GitDiffParser(diff_text)
    file_diffs = parser.parse()

    # --- Semantic analysis ---
    semantic_analyzer = DiffSemanticAnalyzer(file_diffs)
    semantics = semantic_analyzer.analyze()

    # --- Issue extraction ---
    issue = IssueParser(payload.get("pull_request", {}).get("body") or "").parse()

    # --- Classification ---
    classifier = ChangeClassifier(issue, semantics)
    classification = classifier.classify()

    # --- Impact analysis ---

    file_diffs = parser.parse()   # Dict[str, FileDiff]

    total_additions = sum(fd.additions for fd in file_diffs.values())
    total_deletions = sum(fd.deletions for fd in file_diffs.values())

    impact_stats = ImpactStats(
        files_changed=len(file_diffs),
        additions=total_additions,
        deletions=total_deletions,
    )

    impact_analyzer = ImpactAnalyzer(impact_stats)

    # risk = impact_analyzer.risk_level()

    # --- Writing sections ---
    change_section = ChangeWriter(semantics).write()
    context_section = ContextWriter(issue, classification).write()
    impact_section = ImpactWriter(impact_analyzer, classification).write()

    checklist = ChecklistBuilder(classification).build()

    # --- Final markdown ---
    builder = MarkdownBuilder(template)
    return builder.build({
        "change": change_section,
        "context": context_section,
        "impact": impact_section,
        "checklist": checklist,
    })
