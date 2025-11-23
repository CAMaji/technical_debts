import xml.etree.ElementTree as xml

from enum import Enum
from src.utilities.value_range import ValueRange
from src.interface.duplication_report import DuplicationReport

class PMD_CPD_XMLTag(Enum):
    PMD_DUPLICATION_TAG = "{https://pmd-code.org/schema/cpd-report}duplication"
    PMD_FILE_TAG = "{https://pmd-code.org/schema/cpd-report}file"
    PMD_CODE_FRAGMENT_TAG = "{https://pmd-code.org/schema/cpd-report}codefragment"

class PMD_CPD_XmlReader: 
    _reports : list[DuplicationReport]
    _directory : str

    def __init__(self, repo_path : str): 
        self._reports = []
        self._directory = repo_path

        if self._directory.endswith("/") == False:
            self._directory = self._directory + "/"
        return

    def _parse_file_tag(self, pnode : xml.Element, report : DuplicationReport):
        path = pnode.get("path").removeprefix(self._directory)
        line = int(pnode.get("line"))
        endline = int(pnode.get("endline"))
        column = int(pnode.get("column"))
        endcolumn = int(pnode.get("endcolumn"))

        file = DuplicationReport.File(path, ValueRange(line, endline), ValueRange(column, endcolumn))
        report.add_file(file)
        return
    
    def _parse_code_fragment_tag(self, pnode : xml.Element, report : DuplicationReport): 
        report.set_fragment(pnode.text)
        return

    def _parse_duplication_tag(self, pnode : xml.Element):
        lines = int(pnode.attrib['lines'])
        report = DuplicationReport(lines, "")

        for node in pnode:
            if node.tag == PMD_CPD_XMLTag.PMD_FILE_TAG.value:
                self._parse_file_tag(node, report)

            elif node.tag == PMD_CPD_XMLTag.PMD_CODE_FRAGMENT_TAG.value:
                self._parse_code_fragment_tag(node, report)

                # in pmd's xml, <codefragment/> is always the last element
                # inside a <duplication/> container. 
                break

        self._reports.append(report)
        return

    def parse(self, text : str) -> list[DuplicationReport]: 
        root = xml.fromstring(text) 
        for node in root:
            if node.tag == PMD_CPD_XMLTag.PMD_DUPLICATION_TAG.value: 
                self._parse_duplication_tag(node) 
                
        return self._reports
        