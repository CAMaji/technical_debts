import xml.etree.ElementTree as xml
from src.models.duplication_report import DuplicationReport
from enum import Enum

class PmdXmlTag(Enum):
    PMD_DUPLICATION_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}duplication"
    PMD_FILE_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}file"
    PMD_CODE_FRAGMENT_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}codefragment"

class PmdCdpXmlParser: 
    _associations : list[DuplicationReport]
    _repo_path : str

    def __init__(self, repo_path : str): 
        self._associations = []
        self._repo_path = repo_path

        if self._repo_path.endswith("/") == False:
            self._repo_path = self._repo_path + "/"
        return

    def parse_file_tag(self, pnode : xml.Element, report : DuplicationReport):
        path = pnode.get("path").removeprefix(self._repo_path)
        line = int(pnode.get("line"))
        endline = int(pnode.get("endline"))
        column = int(pnode.get("column"))
        endcolumn = int(pnode.get("endcolumn"))
        report.add(path, line, endline, column, endcolumn)
        return
    
    def parse_code_fragment_tag(self, pnode : xml.Element, report : DuplicationReport) -> str: 
        report.fragment = pnode.text
        return

    def parse_duplication_tag(self, pnode : xml.Element):
        lines = int(pnode.attrib['lines'])
        report = DuplicationReport(lines, "")

        for node in pnode:
            if node.tag == PmdXmlTag.PMD_FILE_TAG.value:
                self.parse_file_tag(node, report)

            elif node.tag == PmdXmlTag.PMD_CODE_FRAGMENT_TAG.value:
                self.parse_code_fragment_tag(node, report)

                # in pmd's xml, <codefragment/> is always the last element
                # inside a <duplication/> container.
                break

        self._associations.append(report)
        return

    def parse(self, text : str): 
        root = xml.fromstring(text) 
        for node in root:
            if node.tag == PmdXmlTag.PMD_DUPLICATION_TAG.value: 
                self.parse_duplication_tag(node) 
                
        return
    
    def get_reports(self) -> list[DuplicationReport]:
        return self._associations