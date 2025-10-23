import re 
from dataclasses import dataclass
from typing import List

@dataclass
class Finding:
    name: str         # e.g., "ToDo Fixme comment"
    kind: str         # "Todo found" | "Fixme found"
    start_line: int   # 1-based line number
    

# Analyse the file content as a plain string
def analyse(filename: str, code: str):
    # case-insensitive; accepts "TODO", "Fixme", with/without ":" and trailing text
    pattern = re.compile(r'(?im)\b(?P<tag>todo|fixme)\b\s*:?\s*(?P<rest>.*)')
    findings: List[Finding] = []
    for i, line in enumerate(code.splitlines(), start=1):
        
        m = pattern.search(line)
        if not m:
            continue #if not found then skip code and check next lines  
        tag = m.group('tag').lower()
        kind = "Todo found" if tag == "todo" else "Fixme found"
        findings.append(Finding(
            name="ToDo Fixme comment",
            kind=kind,
            start_line=i
        ))
    return findings
