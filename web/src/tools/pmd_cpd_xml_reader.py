import xml.etree.ElementTree as xml

from enum import Enum
from src.utilities.value_range import ValueRange
from src.reports.duplication_report import DuplicationReport
from src.tools.duplication_report_reader_interface import DupliacationReportReaderInterface

class PMD_CPD_XMLTag(Enum):
    DUPLICATION_TAG = "{https://pmd-code.org/schema/cpd-report}duplication"
    FILE_TAG = "{https://pmd-code.org/schema/cpd-report}file"
    CODE_FRAGMENT_TAG = "{https://pmd-code.org/schema/cpd-report}codefragment"

class PMD_CPD_XmlReader(DupliacationReportReaderInterface): 
    _directory : str

    def __init__(self, repo_path : str): 
        if repo_path.endswith("/"):
            self._directory = repo_path
        else:
            self._directory = repo_path + "/"
        return
    
    def _read_report(self, xmlNode : xml.Element) -> DuplicationReport:
        lines : int = int(xmlNode.attrib["lines"])
        file_list : list[DuplicationReport.File] = []
        fragment : str = ""

        for node in xmlNode:
            if node.tag == PMD_CPD_XMLTag.FILE_TAG.value:
                path      = str(node.get("path").removeprefix(self._directory))
                line      = int(node.get("line"))
                endline   = int(node.get("endline"))
                column    = int(node.get("column"))
                endcolumn = int(node.get("endcolumn"))

                file = DuplicationReport.File(path, ValueRange(line, endline), ValueRange(column, endcolumn))
                file_list.append(file)
                continue

            if node.tag == PMD_CPD_XMLTag.CODE_FRAGMENT_TAG.value:
                fragment = str(node.text)
                break
        
        report = DuplicationReport(lines, fragment)
        for file in file_list:
            report.add_file(file)
            continue

        return report

    def read(self, text : str) -> list[DuplicationReport]:
        report_list = []
        root = xml.fromstring(text) 

        for node in root:
            if node.tag == PMD_CPD_XMLTag.DUPLICATION_TAG.value: 
                report : DuplicationReport = self._read_report(node)
                report_list.append(report)
                continue
     
        return report_list
        