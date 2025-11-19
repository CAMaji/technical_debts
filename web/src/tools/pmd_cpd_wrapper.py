from enum import Enum
from src.tools.tool_wrapper_interface import ToolWrapperInterface
from subprocess import *

# PMD-CDP: https://pmd.github.io/pmd/pmd_userdocs_cpd.html
class PmdCpdWrapper(ToolWrapperInterface): 
    
    # Languages supported by PMD-CPD
    # https://docs.pmd-code.org/latest/tag_languages.html
    class Language(Enum): 
        PYTHON = "python"

    class ReportFormat(Enum):
        XML = "xml"

    minimum_tokens : int
    language : Language
    format : ReportFormat
    dir : str

    def __init__(self, minimum_tokens : int, language : Language, format : ReportFormat, dir : str):
        self.minimum_tokens = minimum_tokens
        self.language = language
        self.format = format
        self.dir = dir
        return
    
    def run(self) -> str: 
        args = [
            "/pmd/pmd-bin-7.18.0/bin/pmd", "cpd", 
            "--minimum-tokens", str(self.minimum_tokens), 
            "--language", self.language.value, 
            "--format", self.format.value, 
            "--dir", self.dir, 
        ]

        done_proc = run(args, capture_output=True, text=True)
        return done_proc.stdout
