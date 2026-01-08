from dataclasses import dataclass
from typing import Dict

from core.diff_semantics import FileSemantics
from core.issue_parser import IssueIntent


@dataclass
class ChangeClassification:
    change_type: str
    breaking: bool
    confidence: str
    rationale: str


class ChangeClassifier:
    """
    Combines issue intent and code semantics to classify PR type.
    """

    def __init__(
        self,
        issue: IssueIntent,
        semantics: Dict[str, FileSemantics]
    ):
        self.issue = issue
        self.semantics = semantics

    def classify(self) -> ChangeClassification:
        breaking = self._detect_breaking()
        behavior_changed = self._behavior_changed()
        formatting_only = self._only_formatting()

        if formatting_only:
            return ChangeClassification(
                change_type="refactor",
                breaking=False,
                confidence="High",
                rationale="Only formatting or non-functional changes detected."
            )

        if behavior_changed:
            if self.issue.intent == "bug":
                return ChangeClassification(
                    change_type="bug fix",
                    breaking=breaking,
                    confidence="High",
                    rationale="Behavioral changes align with bug-related issue."
                )

            if self.issue.intent == "feature":
                return ChangeClassification(
                    change_type="feature",
                    breaking=breaking,
                    confidence="Medium",
                    rationale="Behavioral changes introduce or extend functionality."
                )

        return ChangeClassification(
            change_type="update",
            breaking=breaking,
            confidence="Low",
            rationale="Unable to confidently classify; treated as general update."
        )

    # -------------------------
    # Internal helpers
    # -------------------------

    def _behavior_changed(self) -> bool:
        return any(f.behavior_changed for f in self.semantics.values())

    def _only_formatting(self) -> bool:
        return all(f.only_formatting for f in self.semantics.values())

    def _detect_breaking(self) -> bool:
        for file in self.semantics.values():
            for func in file.functions_changed.values():
                if "signature" in func.change_types:
                    return True
        return False
