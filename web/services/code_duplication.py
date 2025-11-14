from models.code_duplication import *
from models.file_code_duplication import *
from models.model import File
from database.code_duplication_db_facade import *
from tools.pmd_cpd_wrapper import *
from utilities.pmd_cpd_xml_parser import *
import services.file_service as file_service

class CodeDuplicationFileStat: 
    nb_of_duplicated_lines : int
    nb_of_associations : int

    def __init__(self): 
        self.nb_of_associations = 0
        self.nb_of_duplicated_lines = 0


class CodeDuplicationService: 
    db_facade : CodeDuplicationDatabaseFacade

    def __init__(self, db_facade : CodeDuplicationDatabaseFacade): 
        self.db_facade = db_facade

    def insert_one_duplication(self, code_dup : CodeDuplicationModel): 
        self.db_facade.insert_one_duplication(code_dup)

    def insert_many_duplications(self, code_dups : list[CodeDuplicationModel]):
        self.db_facade.insert_many_duplications(code_dups)

    def insert_one_association(self, association : FileCodeDuplicationModel):
        self.db_facade.insert_one_association(association)

    def insert_many_associations(self, associations : list[FileCodeDuplicationModel]): 
        self.db_facade.insert_many_associations(associations)

    def get_duplication_by_id(self, id : str) -> CodeDuplicationModel:
        return self.db_facade.get_duplication_by_id(id)

    def get_association_list_for_file(self, file_id : str) -> list[FileCodeDuplicationModel]:
        return self.db_facade.get_association_list_for_file(file_id)
    
    def get_duplications_by_obj_list(self, obj_list : list[object], id_attrib_name : str) -> list[CodeDuplicationModel]:
        return self.db_facade.get_duplications_by_obj_list(obj_list, id_attrib_name)
    
    def get_file_duplication_association_list(self, file_name : str, file_id : str) -> tuple[str, list[CodeDuplicationModel]]: 
        association_list : list[FileCodeDuplicationModel] = self.get_association_list_for_file(file_id)
        code_dup_list : list[CodeDuplicationModel] = self.get_duplications_by_obj_list(association_list, "code_duplication_id")
        return (file_name, code_dup_list)

    def get_duplications_by_files(self, files : list[File]) -> dict[str, list[CodeDuplicationModel]]: 
        dups_per_file : dict[str, list[CodeDuplicationModel]] = {}
        for f in files: 
            file_code_dup_tuple = self.get_file_duplication_association_list(f.name)
            dups_per_file[file_code_dup_tuple[0]] = file_code_dup_tuple[1]
        return dups_per_file 
    
    def get_stats_for_file(self, file_id : str) -> CodeDuplicationFileStat: 
        association_list : list[FileCodeDuplicationModel] = self.get_association_list_for_file(file_id)
        stats = CodeDuplicationFileStat()

        stats.nb_of_associations = len(association_list)
        for association in association_list: 
            stats.nb_of_duplicated_lines += association.line_count

        return stats

    def get_stats_by_files(self, files : list[File]) -> dict[str, CodeDuplicationFileStat]:
        stats = dict[str, CodeDuplicationFileStat] = {}
        for file in files: 
            stats[file.name] = self.get_stats_for_file(file.id)
        return stats
        

    def run_duplication_analyser(self, minimum_tokens : int, language : PmdCdpLanguage, dir : str): 
        pmd_cpd_wrapper = PmdCpdWrapper(minimum_tokens, language, dir)
        xml_content = pmd_cpd_wrapper.run()

        pmd_cpd_xml_parser = PmdCdpXmlPaser(xml_content, dir)
        pmd_cpd_xml_parser.parse()
        
        code_dup_list : list[CodeDuplicationModel] = []
        for a in pmd_cpd_xml_parser.associations:
            code_dup = CodeDuplicationModel(a.code_fragment)
            code_dup_list.append(code_dup)
            print(code_dup.text)

        self.insert_many_duplications(code_dup_list)

        ass_list : list[FileCodeDuplicationModel] = []
        index = 0
        for a in pmd_cpd_xml_parser.associations: 
            for f in a.files:
                file = file_service.get_file_by_filename(f)
                association = FileCodeDuplicationModel(code_dup_list[index].id, file.id, a.lines)
                ass_list.append(association)

        self.insert_many_associations(ass_list) 
        return
