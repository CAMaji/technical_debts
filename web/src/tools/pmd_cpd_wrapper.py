from enum import Enum
from subprocess import *

# Languages supported by PMD-CPD
# https://docs.pmd-code.org/latest/tag_languages.html
class PmdCdpLanguage(Enum): 
    PYTHON = "python"

# PMD-CDP: https://pmd.github.io/pmd/pmd_userdocs_cpd.html
class PmdCpdWrapper: 
    minimum_tokens : int
    language : PmdCdpLanguage
    format : str
    dir : str

    def __init__(self, minimum_tokens : int, language : PmdCdpLanguage, dir : str):
        self.minimum_tokens = minimum_tokens
        self.language = language
        self.format = "xml"
        self.dir = dir
        return
    
    def run(self) -> str: 
        args = [
            "/pmd/pmd-bin-7.18.0/bin/pmd", "cpd", 
            "--minimum-tokens", str(self.minimum_tokens), 
            "--language", self.language.value, 
            "--format", self.format, 
            "--dir", self.dir, 
        ]

        done_proc = run(args, capture_output=True, text=True)
        return done_proc.stdout
