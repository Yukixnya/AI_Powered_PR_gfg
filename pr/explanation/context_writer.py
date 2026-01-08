from pr.core.issue_parser import IssueIntent
from pr.core.change_classifier import ChangeClassification


class ContextWriter:
    """
    Writes the 'Context' / 'Why' section of the PR.
    """

    def __init__(
        self,
        issue: IssueIntent,
        classification: ChangeClassification
    ):
        self.issue = issue
        self.classification = classification

    def write(self) -> str:
        lines = []

        lines.append(
            f"This pull request addresses the following problem:\n\n"
            f"> {self.issue.summary}"
        )

        lines.append("")
        lines.append(self._explain_motivation())

        # 👇 NEW: Explicit reassurance for refactors
        if self.classification.change_type == "refactor":
            lines.append("")
            lines.append(
                "No functional behavior is changed as part of this update."
            )

        if self.issue.constraints:
            lines.append("")
            lines.append("**Constraints considered:**")
            for c in self.issue.constraints:
                lines.append(f"- {c}")

        return "\n".join(lines)

    def _explain_motivation(self) -> str:
        ct = self.classification.change_type

        if ct == "bug fix":
            return (
                "The existing behavior did not fully align with the expected "
                "functionality, leading to incorrect outcomes. This change "
                "corrects that behavior while preserving the original design intent."
            )

        if ct == "feature":
            return (
                "The current implementation lacked support for the described "
                "use case. This update extends existing behavior in a "
                "backward-compatible manner."
            )

        if ct == "refactor":
            return (
                "This change improves internal structure and readability "
                "to make the code easier to understand and maintain."
            )

        return (
            "This update aligns the implementation more closely with the "
            "intended behavior and project standards."
        )
