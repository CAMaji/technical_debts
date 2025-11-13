import uuid
import file_service as file_service
from models.code_duplication import *
from models.file_code_duplication import *
from models.model import *
from sqlalchemy import select, delete, literal_column, Row
from subprocess import *
from xml.etree.ElementTree import *
from app import db
from enum import Enum

# Languages supported by PMD-CPD
# https://docs.pmd-code.org/latest/tag_languages.html
class PMD_Language(Enum): 
    PYTHON = "python"

class PMD_XmlTag(Enum):
    PMD_DUPLICATION_TAG = "{https://pmd-code.org/schema/cpd-report}duplication"
    PMD_FILE_TAG = "{https://pmd-code.org/schema/cpd-report}file"
    PMD_CODE_FRAGMENT_TAG = "{https://pmd-code.org/schema/cpd-report}codefragment"

class PMD_ParsedFileData: 
    path : str
    line_count : int

class FCD_Stats:
    filename : str
    duplication_count : int
    lines_duplicated : int

class FCD_Aggregated_Stats:
    max_duplication_count : int
    max_duplicated_lines : int
    avg_duplication_count : float
    avg_duplicated_lines : float
    sum_duplication_count : int
    sum_duplicated_lines : int
    stats : list[FCD_Stats]

class CodeDuplicationService: 
    def create(self, text: str) -> CodeDuplicationModel:
        id : str = str(uuid.uuid4())
        code_dup_model = CodeDuplicationModel(id = id, text = text)
        return code_dup_model

    def insert(self, code_dup_model : CodeDuplicationModel): 
        db.session.add(code_dup_model)
        db.session.commit()

    def insert_batch(self, code_dup_list : list[CodeDuplicationModel]):
        for cd in code_dup_list: 
            db.session.add(cd)
        db.session.commit()

    def create_association(self, code_dup_id : str, file_id : str, line_count : int) -> FileCodeDuplicationModel: 
        id : str = str(uuid.uuid4())
        file_code_dup_model = FileCodeDuplicationModel(id=id, file_id=file_id, code_duplication_id=code_dup_id, line_count=line_count)
        return file_code_dup_model

    def insert_association(self, file_code_dup_association : FileCodeDuplicationModel):
        db.session.add(file_code_dup_association)
        db.session.commit()

    def insert_association_batch(self, file_code_dup_association : list[FileCodeDuplicationModel]): 
        for fcd in file_code_dup_association: 
            db.session.add(fcd)
        db.session.commit()

    def get_code_duplication_for_id(self, id : str) -> CodeDuplicationModel: 
        return db.session.query(CodeDuplicationModel).filter_by(id=id).first()

    def get_association_list_for_file(self, file : File) -> list[FileCodeDuplicationModel]:
        return db.session.query(FileCodeDuplicationModel).filter_by(file_id=file.id).all()

    def get_code_duplication_query_for_files(self, files : list[File]) -> dict[str, list[CodeDuplicationModel]]: 
        _dict : dict[str, list[CodeDuplicationModel]] = {}
        for f in files: 
            _list : list[FileCodeDuplicationModel] = self.get_association_list_for_file(f)
            _dict[f.name] = list()
            for fcd in _list:
                code_dup = self.get_code_duplication_for_id(fcd.code_duplication_id)
                _dict[f.name].append(code_dup)
        return _dict

    def __analyser_parse_duplication_node__(self, node : Element[str], repo_path : str): 
        list_of_file : list[PMD_ParsedFileData] = []
        list_of_code_dup : list[CodeDuplicationModel] = []
        list_of_associations : list[FileCodeDuplicationModel] = []

        for sub_node in node: 
            if sub_node.tag == PMD_XmlTag.PMD_FILE_TAG : # <file>                        
                file_path = sub_node.get("path").removeprefix(repo_path) # Doit terminer avec '/'
                line_count = sub_node.get("endline") - sub_node.get("line")
                file_data = PMD_ParsedFileData(path=file_path, line_count=line_count)
                list_of_file.append(file_data)

            elif sub_node.tag == PMD_XmlTag.PMD_CODE_FRAGMENT_TAG: # <code fragment>
                code_dup = self.create(sub_node.text)
                for fr in list_of_file:
                    association = self.create_association(fr.id, code_dup.id,)
                    list_of_associations.append(association)
                list_of_code_dup.append(code_dup)
        return
    
    def launch_analyser_tool(self, path : str, language_list : list[PMD_Language], minimum_token : int):
        for lang in language_list:
            pmd_cmd : list[str] = [
                "./tools/pmd/bin/pmd", "cpd", 
                "--minimum-tokens", str(minimum_token), 
                "--language", lang, 
                "--format", "xml", 
                "--dir", path
            ]

            completed : CompletedProcess = run(pmd_cmd, capture_output=True, text=True)
            root : Element[str] = ElementTree.fromstring(completed.stdout)
            for node in root:
                if node.tag == PMD_XmlTag.PMD_DUPLICATION_TAG: # <duplication>
                    self.__analyser_parse_duplication_node__(node, path)
        return
    
    def get_duplication_stats_for_files(self, files : list[File]) -> FCD_Aggregated_Stats: 
        stats_list : list[FCD_Stats] = []
        max_lines_dupd = 0
        max_nb_dupd = 0
        sum_lines_dupd = 0
        sum_dup = 0

        for f in files: 
            _dict : dict[str, int] = dict()
            _list : list[FileCodeDuplicationModel] = self.get_fcd_from_file(f)
            lines_dupd : int = 0

            for fcd in _list: 
                lines_dupd += fcd.line_count
                sum_lines_dupd += fcd.line_count

            nb_dup = _list.count()
            sum_dup += nb_dup

            if max_lines_dupd < lines_dupd:
                max_lines_dupd = lines_dupd
            if max_nb_dupd < nb_dup:
                max_nb_dupd = nb_dup

            stats = FCD_Stats(filename=f.name, duplication_count=nb_dup, lines_duplicated=lines_dupd)
            stats_list.append(stats)
        
        avg_lines_dupd = sum_lines_dupd / files.count()
        avg_dup = sum_dup / files.count()
        agg_stats = FCD_Aggregated_Stats(
            max_duplication_count=max_nb_dupd,
            max_duplicated_lines=max_lines_dupd,
            avg_duplication_count=avg_dup,
            avg_duplicated_lines=avg_lines_dupd,
            sum_duplication_count=sum_dup,
            sum_duplicated_lines=sum_lines_dupd,
            stats=stats_list
        )
        return agg_stats

    #def optimised__get_duplications_for_files(self, commit_id : str):
    #    f_sub_qry = db.session.query(File.id.label("file_id"), File.name.label("file_name"))
    #    f_sub_qry = f_sub_qry.join(Commit)
    #    f_sub_qry = f_sub_qry.where(File.commit_id==commit_id)
    #    f_sub_qry = f_sub_qry.subquery("f")
    #
    #    d_qry = db.session.query(f_sub_qry.columns.file_id, f_sub_qry.columns.file_name, CodeDuplicationModel.code_duplication_id, CodeDuplicationModel.text)
    #    d_qry = d_qry.join(f_sub_qry, FileCodeDuplicationModel.file_id == f_sub_qry.file_id)
    #    d_qry = d_qry.join(CodeDuplicationModel, FileCodeDuplicationModel.code_duplication_id == CodeDuplicationModel.id)
    #
    #    result = d_qry.all()
    #    return result
        



        
        
            
        
        
    

    

