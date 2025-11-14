from models.code_duplication import CodeDuplicationModel
from models.file_code_duplication import FileCodeDuplicationModel
from database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from typing import Callable

class CodeDuplicationDatabaseFacadeMock(CodeDuplicationDatabaseFacade): 
    insert_one_duplication_hook         : Callable[[CodeDuplicationModel], None]
    insert_one_association_hook         : Callable[[FileCodeDuplicationModel], None]
    insert_many_duplications_hook       : Callable[[list[CodeDuplicationModel]], None]
    insert_many_associations_hook       : Callable[[list[FileCodeDuplicationModel]], None]
    get_duplication_by_id_hook          : Callable[[str], CodeDuplicationModel]
    get_associations_for_one_file_hook  : Callable[[str], list[FileCodeDuplicationModel]]
    get_duplications_for_many_objs_hook   : Callable[[list[object], str], list[CodeDuplicationModel]]

    def __init__(self): 
        super().__init__()
        self.insert_one_duplication_hook         = None
        self.insert_one_association_hook         = None
        self.insert_many_duplications_hook       = None
        self.insert_many_associations_hook       = None
        self.get_duplication_by_id_hook          = None
        self.get_associations_for_one_file_hook  = None
        self.get_duplications_for_many_objs_hook = None

    def insert_one_duplication(self, code_dup : CodeDuplicationModel):
        self.insert_one_duplication_hook(code_dup)
    
    def insert_one_association(self, association : FileCodeDuplicationModel):
        self.insert_one_association_hook(association)

    def insert_many_duplications(self, code_dups : list[CodeDuplicationModel]): 
        return self.insert_many_duplications_hook(code_dups)

    def insert_many_associations(self, associations : list[FileCodeDuplicationModel]):
        return self.insert_many_associations_hook(associations)

    def get_duplication_by_id(self, id : str) -> CodeDuplicationModel:
        return self.get_duplication_by_id_hook(id)
    
    def get_associations_for_one_file(self, file_id : str) -> list[FileCodeDuplicationModel]: 
        return self.get_associations_for_one_file_hook(file_id)
    
    def get_duplications_for_many_objs(self, obj_list : list[object], attrib_name : str) -> list[CodeDuplicationModel]: 
        return self.get_duplications_for_many_objs_hook(obj_list, attrib_name)