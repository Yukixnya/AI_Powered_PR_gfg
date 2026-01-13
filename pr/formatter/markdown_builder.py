from typing import Dict


class MarkdownBuilder:
    """
    Assembles the final PR markdown using templates.
    """

    def __init__(self, template: str):
        self.template = template

    def build(self, sections: Dict[str, str]) -> str:
        output = self.template
        for key, value in sections.items():
            output = output.replace(f"{{{{{key}}}}}", value.strip())
        return output.strip()
