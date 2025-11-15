from models.code_duplication import *
from models.file_code_duplication import *
from models.model import File
from database.code_duplication_db_facade import *
from tools.pmd_cpd_wrapper import *
from utilities.pmd_cpd_xml_parser import *
from utilities.custom_json_encoder import *

import services.file_service as file_service

class CodeDuplicationFileStat(CustomJsonEncoder): 
    nb_of_duplicated_lines : int
    nb_of_associations : int

    def __init__(self): 
        self.nb_of_associations = 0
        self.nb_of_duplicated_lines = 0

    def encode(self):
        return {
            "nb_of_duplicated_lines": self.nb_of_duplicated_lines,
            "nb_of_associations": self.nb_of_associations
        }


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
    
    # id_attrib_name = the name of the object's attribute that contains a valid code duplication id.
    # In other words, the name of the instance variable that has a code duplication id. 
    def get_duplications_for_many_objs(self, obj_list : list[object], id_attrib_name : str) -> list[CodeDuplicationModel]:
        return self.db_facade.get_duplications_for_many_objs(obj_list, id_attrib_name)
    
    def get_duplications_for_one_file(self, file_id : str) -> list[CodeDuplicationModel]:
        association_list : list[FileCodeDuplicationModel] = self.get_associations_for_one_file(file_id)
        code_dup_list : list[CodeDuplicationModel] = self.get_duplications_for_many_objs(association_list, "code_duplication_id")
        return code_dup_list

    def get_associations_for_one_file(self, file_id : str) -> list[FileCodeDuplicationModel]:
        return self.db_facade.get_associations_for_one_file(file_id)
    
    def get_duplications_for_many_files(self, files : list[File]) -> dict[str, list[CodeDuplicationModel]]: 
        dups_per_file : dict[str, list[CodeDuplicationModel]] = {}
        for f in files: 
            code_dup_list = self.get_duplications_for_one_file(f.id)
            dups_per_file[f.name] = code_dup_list
        return dups_per_file 
    
    def get_stats_for_one_file(self, file_id : str) -> CodeDuplicationFileStat: 
        association_list : list[FileCodeDuplicationModel] = self.get_associations_for_one_file(file_id)
        stats = CodeDuplicationFileStat()

        stats.nb_of_associations = len(association_list)
        for association in association_list: 
            stats.nb_of_duplicated_lines += association.line_count

        return stats

    def get_stats_for_many_files(self, files : list[File]) -> dict[str, CodeDuplicationFileStat]:
        stats : dict[str, CodeDuplicationFileStat] = {}
        for file in files: 
            stats[file.name] = self.get_stats_for_one_file(file.id)
        return stats
        
    def run_duplication_analyser(self, minimum_tokens : int, language : PmdCdpLanguage, dir : str): 
        pmd_cpd_wrapper = PmdCpdWrapper(minimum_tokens, language, dir)
        xml_content = pmd_cpd_wrapper.run()

        pmd_cpd_xml_parser = PmdCdpXmlParser(xml_content, dir)
        pmd_cpd_xml_parser.parse()
        
        code_dup_list : list[CodeDuplicationModel] = []
        for a in pmd_cpd_xml_parser.associations:
            code_dup = CodeDuplicationModel(a.code_fragment)
            code_dup_list.append(code_dup)

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
