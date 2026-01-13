from dataclasses import dataclass
from typing import Optional


@dataclass
class ImpactStats:
    files_changed: int
    additions: int
    deletions: int


class ImpactAnalyzer:
    """
    Analyzes the overall impact and risk of a PR based on change size and spread.
    """

    def __init__(self, stats):
        """
        stats: FileDiff or None
        """
        self.stats = stats

    def risk_level(self) -> str:
        if not self.stats:
            return "Low"

        churn = self.stats.additions + self.stats.deletions

        if churn < 50:
            return "Low"
        if churn < 200:
            return "Medium"
        return "High"

    def scope(self) -> str:
        if not self.stats:
            return "Localized"

        # FileDiff represents one file; broader scope handled earlier
        return "Localized"
