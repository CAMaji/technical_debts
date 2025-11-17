from src.models.code_duplication import CodeDuplicationModel
from src.models.file_code_duplication import FileCodeDuplicationModel
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from typing import Callable

class CodeDuplicationDatabaseFacadeHooks:
    insert_one_duplication         : Callable[[CodeDuplicationModel], None]
    insert_one_association         : Callable[[FileCodeDuplicationModel], None]
    insert_many_duplications       : Callable[[list[CodeDuplicationModel]], None]
    insert_many_associations       : Callable[[list[FileCodeDuplicationModel]], None]
    get_duplication_by_id          : Callable[[str], CodeDuplicationModel]
    get_associations_for_one_file  : Callable[[str], list[FileCodeDuplicationModel]]
    get_duplications_for_many_objs : Callable[[list[object], str], list[CodeDuplicationModel]]

    def __init__(self):
        # I was too lazy to set every hook to None by hand.
        for _var in self.__dict__:
            setattr(self, _var, None)
        return

class CodeDuplicationDatabaseFacadeMock(CodeDuplicationDatabaseFacade): 
    hooks : CodeDuplicationDatabaseFacadeHooks

    def __init__(self): 
        self.hooks = CodeDuplicationDatabaseFacadeHooks()
        return

    def insert_one_duplication(self, code_dup : CodeDuplicationModel):
        self.hooks.insert_one_duplication(code_dup)
    
    def insert_one_association(self, association : FileCodeDuplicationModel):
        self.hooks.insert_one_association(association)

    def insert_many_duplications(self, code_dups : list[CodeDuplicationModel]): 
        return self.hooks.insert_many_duplications(code_dups)

    def insert_many_associations(self, associations : list[FileCodeDuplicationModel]):
        return self.hooks.insert_many_associations(associations)

    def get_duplication_by_id(self, id : str) -> CodeDuplicationModel:
        return self.hooks.get_duplication_by_id(id)
    
    def get_associations_for_one_file(self, file_id : str) -> list[FileCodeDuplicationModel]: 
        return self.hooks.get_associations_for_one_file(file_id)
    
    def get_duplications_for_many_objs(self, obj_list : list[object], attrib_name : str) -> list[CodeDuplicationModel]: 
        return self.hooks.get_duplications_for_many_objs(obj_list, attrib_name)