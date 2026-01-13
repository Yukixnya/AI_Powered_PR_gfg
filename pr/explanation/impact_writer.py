from core.impact_analyzer import ImpactAnalyzer
from core.change_classifier import ChangeClassification


class ImpactWriter:
    """
    Writes the 'Risk & Impact' section.
    """

    def __init__(
        self,
        impact: ImpactAnalyzer,
        classification: ChangeClassification
    ):
        self.impact = impact
        self.classification = classification

    def write(self) -> str:
        lines = []

        lines.append(f"- **Risk level:** {self.impact.risk_level()}")
        lines.append(f"- **Change scope:** {self.impact.scope()}")

        if self.classification.breaking:
            lines.append(
                "- **Breaking change:** Yes (function signatures were modified)"
            )
        else:
            lines.append("- **Breaking change:** No")

        lines.append("")
        lines.append("**Review focus:**")
        lines.append(self._review_guidance())

        return "\n".join(lines)

    def _review_guidance(self) -> str:
        risk = self.impact.risk_level()

        if risk == "Low":
            return (
                "- Verify no functional behavior has changed\n"
                "- Ensure formatting aligns with project conventions"
            )

        if risk == "Medium":
            return (
                "- Review updated logic paths carefully\n"
                "- Pay attention to edge cases and related components"
            )

        return (
            "- Perform a thorough review of logic and control flow\n"
            "- Consider downstream and integration impact"
        )
