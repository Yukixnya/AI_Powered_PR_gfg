import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from pr.core.diff_parser import FileDiff, DiffHunk


# -----------------------------
# Semantic data structures
# -----------------------------

@dataclass
class FunctionChange:
    name: str
    added_lines: int = 0
    removed_lines: int = 0
    change_types: Set[str] = field(default_factory=set)


@dataclass
class FileSemantics:
    filename: str
    functions_changed: Dict[str, FunctionChange] = field(default_factory=dict)
    classes_changed: Set[str] = field(default_factory=set)
    behavior_changed: bool = False
    only_formatting: bool = True
    total_logic_changes: int = 0


# -----------------------------
# Semantic Analyzer
# -----------------------------

class DiffSemanticAnalyzer:
    """
    Interprets diff hunks and extracts meaning:
    - Which functions are impacted
    - Whether logic or behavior changed
    - Nature of the changes
    """

    FUNC_DEF_RE = re.compile(r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)")
    CLASS_DEF_RE = re.compile(r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)")

    LOGIC_KEYWORDS = (
        "if ", "elif ", "else:",
        "return ", "raise ",
        "for ", "while ",
        "try:", "except ",
        "and ", "or ",
    )

    def __init__(self, parsed_diff: Dict[str, FileDiff]):
        self.parsed_diff = parsed_diff

    def analyze(self) -> Dict[str, FileSemantics]:
        result: Dict[str, FileSemantics] = {}

        for filename, file_diff in self.parsed_diff.items():
            semantics = FileSemantics(filename=filename)

            current_function = None
            current_class = None

            for hunk in file_diff.hunks:
                # Analyze context first (to know where we are)
                for ctx in hunk.context_lines:
                    func_match = self.FUNC_DEF_RE.search(ctx)
                    class_match = self.CLASS_DEF_RE.search(ctx)

                    if func_match:
                        current_function = func_match.group(1)
                    if class_match:
                        current_class = class_match.group(1)
                        semantics.classes_changed.add(current_class)

                # Analyze added lines
                for line in hunk.added_lines:
                    self._process_line(
                        line=line,
                        semantics=semantics,
                        function=current_function,
                        is_addition=True
                    )

                # Analyze removed lines
                for line in hunk.removed_lines:
                    self._process_line(
                        line=line,
                        semantics=semantics,
                        function=current_function,
                        is_addition=False
                    )

            result[filename] = semantics

        return result

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _process_line(
        self,
        line: str,
        semantics: FileSemantics,
        function: str,
        is_addition: bool
    ):
        stripped = line.strip()

        # Ignore empty lines
        if not stripped:
            return

        # Comment-only change
        if stripped.startswith("#"):
            return

        # Formatting-only change
        if stripped in ("pass",):
            return

        # Now we assume real logic
        semantics.only_formatting = False

        if function:
            if function not in semantics.functions_changed:
                semantics.functions_changed[function] = FunctionChange(name=function)

            func_change = semantics.functions_changed[function]

            if is_addition:
                func_change.added_lines += 1
            else:
                func_change.removed_lines += 1

            # Detect logic type
            for kw in self.LOGIC_KEYWORDS:
                if kw in stripped:
                    func_change.change_types.add("logic")
                    semantics.total_logic_changes += 1
                    semantics.behavior_changed = True

            # Detect signature change
            if stripped.startswith("def "):
                func_change.change_types.add("signature")
                semantics.behavior_changed = True

            # Detect return modification
            if stripped.startswith("return"):
                func_change.change_types.add("return")
                semantics.behavior_changed = True
