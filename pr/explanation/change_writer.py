from typing import Dict
from pr.core.diff_semantics import FileSemantics


class ChangeWriter:
    """
    Writes the 'What Changed' section.
    """

    def __init__(self, semantics: Dict[str, FileSemantics]):
        self.semantics = semantics

    def write(self) -> str:
        lines = []

        for filename, file_sem in self.semantics.items():
            lines.append(f"### `{filename}`")

            # 👇 NEW: Explicit formatting-only explanation
            if file_sem.only_formatting:
                lines.append(
                    "- Formatting-only adjustments to improve readability "
                    "and consistency; no logic changes."
                )
                lines.append("")
                continue

            if not file_sem.functions_changed:
                lines.append(
                    "- Internal cleanup and small structural improvements "
                    "without functional changes."
                )
                lines.append("")
                continue

            for func_name, func_change in file_sem.functions_changed.items():
                description = self._describe_function_change(func_change)
                lines.append(f"- **{func_name}**: {description}")

            lines.append("")

        return "\n".join(lines)

    def _describe_function_change(self, func_change) -> str:
        parts = []

        if "signature" in func_change.change_types:
            parts.append("function signature updated")

        if "logic" in func_change.change_types:
            parts.append("conditional or control flow logic adjusted")

        if "return" in func_change.change_types:
            parts.append("return behavior modified")

        if not parts:
            parts.append("internal implementation refined")

        added = func_change.added_lines
        removed = func_change.removed_lines

        return f"{', '.join(parts)} (+{added}/-{removed} lines)"
