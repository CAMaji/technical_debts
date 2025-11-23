from enum import Enum
from src.tools.tool_interface import ToolInterface
from subprocess import *

# PMD-CDP: https://pmd.github.io/pmd/pmd_userdocs_cpd.html
class PMD_CopyPasteDetector(ToolInterface): 
    
    # Languages supported by PMD-CPD
    # https://docs.pmd-code.org/latest/tag_languages.html
    class Language(Enum): 
        PYTHON = "python"

    class ReportFormat(Enum):
        XML = "xml"

    minimum_tokens : int
    languages : list[Language]
    format : ReportFormat
    dir : str

    def __init__(self, minimum_tokens : int, languages : list[Language], format : ReportFormat, dir : str):
        self.minimum_tokens = minimum_tokens
        self.languages = languages
        self.format = format
        self.dir = dir
        return
    
    def run(self) -> list[str]: 
        output_list = []
        for lang in self.languages:
            args = [
                "/pmd/pmd-bin-7.18.0/bin/pmd", "cpd", 
                "--minimum-tokens", str(self.minimum_tokens), 
                "--language", lang.value, 
                "--format", self.format.value, 
                "--dir", self.dir, 
            ]

            done_proc = run(args, capture_output=True, text=True)
            output_list.append(done_proc.stdout)
        return output_list
