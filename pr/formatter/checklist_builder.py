from core.change_classifier import ChangeClassification


class ChecklistBuilder:
    """
    Builds a reviewer checklist based on change classification.
    """

    def __init__(self, classification: ChangeClassification):
        self.classification = classification

    def build(self) -> str:
        items = [
            "Changes are scoped to the stated problem",
            "No unrelated modifications included",
            "Code follows project conventions",
        ]

        if self.classification.breaking:
            items.append("Breaking changes are documented and justified")

        if self.classification.change_type == "bug fix":
            items.append("Fix covers the reported failure mode")

        if self.classification.change_type == "feature":
            items.append("New behavior is backward-compatible")

        return "\n".join(f"- [x] {item}" for item in items)
