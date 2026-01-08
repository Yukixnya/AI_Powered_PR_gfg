import re
from dataclasses import dataclass
from typing import List


@dataclass
class IssueIntent:
    raw_text: str
    summary: str
    intent: str
    constraints: List[str]


class IssueParser:
    """
    Parses issue / ticket / description text.
    Extracts intent and constraints in a conservative manner.
    """

    BUG_KEYWORDS = (
        "bug", "error", "incorrect", "fails", "failure",
        "broken", "unexpected", "crash"
    )

    FEATURE_KEYWORDS = (
        "add", "implement", "support", "introduce", "enable"
    )

    REFACTOR_KEYWORDS = (
        "refactor", "cleanup", "optimize", "restructure", "simplify"
    )

    CONSTRAINT_PATTERNS = (
        r"must\s+not\s+[\w\s]+",
        r"should\s+not\s+[\w\s]+",
        r"without\s+[\w\s]+",
        r"ensure\s+that\s+[\w\s]+",
    )

    def __init__(self, issue_text: str):
        self.text = issue_text.strip()

    def parse(self) -> IssueIntent:
        lowered = self.text.lower()

        intent = "update"

        if self._contains_any(lowered, self.BUG_KEYWORDS):
            intent = "bug"
        elif self._contains_any(lowered, self.FEATURE_KEYWORDS):
            intent = "feature"
        elif self._contains_any(lowered, self.REFACTOR_KEYWORDS):
            intent = "refactor"

        summary = self._extract_summary(self.text)
        constraints = self._extract_constraints(self.text)

        return IssueIntent(
            raw_text=self.text,
            summary=summary,
            intent=intent,
            constraints=constraints,
        )

    # -------------------------
    # Internal helpers
    # -------------------------

    def _contains_any(self, text: str, keywords) -> bool:
        return any(k in text for k in keywords)

    def _extract_summary(self, text: str) -> str:
        """
        Use first meaningful sentence as summary.
        """
        sentences = re.split(r"[.!?\n]", text)
        for s in sentences:
            cleaned = s.strip()
            if len(cleaned) > 10:
                return cleaned
        return text.strip()

    def _extract_constraints(self, text: str) -> List[str]:
        constraints = []
        lowered = text.lower()

        for pattern in self.CONSTRAINT_PATTERNS:
            matches = re.findall(pattern, lowered)
            constraints.extend(matches)

        return constraints
