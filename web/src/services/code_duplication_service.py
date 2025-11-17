from src.models.code_duplication import *
from src.models.file_code_duplication import *
from src.models.model import File
from src.database.code_duplication_db_facade import *
from src.tools.pmd_cpd_wrapper import *
from src.utilities.pmd_cpd_xml_parser import *
from src.utilities.custom_json_encoder import *

class CodeDuplicationFileStat(CustomJsonEncoder): 
    nb_of_duplicated_lines : int
    nb_of_associations : int

    def __init__(self): 
        self.nb_of_associations = 0
        self.nb_of_duplicated_lines = 0

    def encode(self):
        return {
            "nb_of_duplicated_lines": self.nb_of_duplicated_lines,
            "nb_of_duplications": self.nb_of_associations
        }

class CodeDuplicationService: 
    _facade : CodeDuplicationDatabaseFacade

    def __init__(self, db_facade : CodeDuplicationDatabaseFacade): 
        self._facade = db_facade

    def insert_one_duplication(self, code_dup : CodeDuplicationModel): 
        self._facade.insert_one_duplication(code_dup)

    def insert_many_duplications(self, code_dups : list[CodeDuplicationModel]):
        self._facade.insert_many_duplications(code_dups)

    def insert_one_association(self, association : FileCodeDuplicationModel):
        self._facade.insert_one_association(association)

    def insert_many_associations(self, associations : list[FileCodeDuplicationModel]): 
        self._facade.insert_many_associations(associations)

    def get_duplication_by_id(self, id : str) -> CodeDuplicationModel:
        return self._facade.get_duplication_by_id(id)
    
    # id_attrib_name = the name of the object's attribute that contains a valid code duplication id.
    # In other words, the name of the instance variable that has an ID of code duplication row. 
    def get_duplications_for_many_objs(self, obj_list : list[object], code_duplication_id_attribute : str) -> list[CodeDuplicationModel]:
        return self._facade.get_duplications_for_many_objs(obj_list, code_duplication_id_attribute)
    
    def get_duplications_for_one_file(self, file_id : str) -> list[CodeDuplicationModel]:
        association_list : list[FileCodeDuplicationModel] = self.get_associations_for_one_file(file_id)
        code_dup_list : list[CodeDuplicationModel] = self.get_duplications_for_many_objs(association_list, "code_duplication_id")
        return code_dup_list

    def get_associations_for_one_file(self, file_id : str) -> list[FileCodeDuplicationModel]:
        return self._facade.get_associations_for_one_file(file_id)
    
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
          
    def run_duplication_analyser(self, pmd_cpd_wrapper : PmdCpdWrapper, pmd_cpd_xml_parser : PmdCdpXmlParser, files : list[File]): 
        file_registry : dict[str, File] = {}
        for f in files: 
            file_registry[f.name] = f

        xml_content = pmd_cpd_wrapper.run()
        pmd_cpd_xml_parser.parse(xml_content)
        
        code_dup_list : list[CodeDuplicationModel] = []
        for a in pmd_cpd_xml_parser.associations:
            code_dup = CodeDuplicationModel(a.code_fragment)
            code_dup_list.append(code_dup)

        self.insert_many_duplications(code_dup_list)

        ass_list : list[FileCodeDuplicationModel] = []
        index = 0
        for a in pmd_cpd_xml_parser.associations: 
            for f in a.files:
                file = file_registry[f]
                association = FileCodeDuplicationModel(code_dup_list[index].id, file.id, a.lines)
                ass_list.append(association)

        self.insert_many_associations(ass_list) 
        return
