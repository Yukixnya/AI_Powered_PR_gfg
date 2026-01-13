import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DiffHunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    context_lines: List[str] = field(default_factory=list)


@dataclass
class FileDiff:
    filename: str
    hunks: List[DiffHunk] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0


class GitDiffParser:
    """
    Parses a unified git diff into structured objects.
    No assumptions. No heuristics. Pure parsing.
    """

    HUNK_HEADER = re.compile(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")

    def __init__(self, diff_text: str):
        self.diff_text = diff_text
        self.files: Dict[str, FileDiff] = {}

    def parse(self) -> Dict[str, FileDiff]:
        current_file: Optional[FileDiff] = None
        current_hunk: Optional[DiffHunk] = None

        for raw_line in self.diff_text.splitlines():
            line = raw_line.rstrip("\n")

            # Detect file
            if line.startswith("+++ b/"):
                filename = line.replace("+++ b/", "").strip()
                current_file = FileDiff(filename=filename)
                self.files[filename] = current_file
                current_hunk = None
                continue

            # Detect hunk
            hunk_match = self.HUNK_HEADER.match(line)
            if hunk_match and current_file:
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2) or "1")
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4) or "1")

                current_hunk = DiffHunk(
                    old_start=old_start,
                    old_count=old_count,
                    new_start=new_start,
                    new_count=new_count,
                )
                current_file.hunks.append(current_hunk)
                continue

            # Inside hunk
            if current_hunk:
                if line.startswith("+") and not line.startswith("+++"):
                    current_hunk.added_lines.append(line[1:])
                    current_file.additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    current_hunk.removed_lines.append(line[1:])
                    current_file.deletions += 1
                else:
                    current_hunk.context_lines.append(line)

        return self.files
