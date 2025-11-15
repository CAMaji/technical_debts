import xml.etree.ElementTree as xml
from models.code_duplication import *
from models.file_code_duplication import *
from enum import Enum

class PmdXmlTag(Enum):
    PMD_DUPLICATION_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}duplication"
    PMD_FILE_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}file"
    PMD_CODE_FRAGMENT_TAG = "{" + "https://pmd-code.org/schema/cpd-report" + "}codefragment"

class PmdCdpAssociations: 
    lines : int
    files : list[str]
    code_fragment : str

    def __init__(self):
        self.lines = -1
        self.files = []
        self.code_fragment = ""
        return

class PmdCdpXmlParser: 
    associations : list[PmdCdpAssociations]
    current : PmdCdpAssociations
    text : str
    repo_path : str

    def __init__(self, text : str, repo_path : str): 
        self.associations = []
        self.text = text
        self.repo_path = repo_path
        self.current = None

        if self.repo_path.endswith("/") == False:
            self.repo_path = self.repo_path + "/"
        return

    def parse_file_tag(self, pnode : xml.Element):
        if pnode.tag != PmdXmlTag.PMD_FILE_TAG.value:
            return
    
        path = pnode.get("path").removeprefix(self.repo_path)
        self.current.files.append(path)
        return
    
    def parse_code_fragment_tag(self, pnode : xml.Element): 
        if pnode.tag != PmdXmlTag.PMD_CODE_FRAGMENT_TAG.value:
            return 
        
        self.current.code_fragment = pnode.text
        return
        

    def parse_duplication_tag(self, pnode : xml.Element):
        if pnode.tag != PmdXmlTag.PMD_DUPLICATION_TAG.value: 
            return

        self.current = PmdCdpAssociations()
        self.current.lines = int(pnode.get("lines"))

        for node in pnode:
            self.parse_file_tag(node)
            self.parse_code_fragment_tag(node)
            
        self.associations.append(self.current)
        self.current = None 
        return

    def parse(self): 
        root = xml.fromstring(self.text) 
        for node in root:
            self.parse_duplication_tag(node) 
        return