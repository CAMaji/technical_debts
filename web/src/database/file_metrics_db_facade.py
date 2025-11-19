from src.models.model import db, Complexity, Function, IdentifiableEntity, FileIdentifiableEntity
from src.models.code_fragment import CodeFragment
from src.models.duplication import Duplication
from typing import TypeAlias
from src.utilities.facade_utilities import FacadeUtilities

# type aliases for clarity
FileID_str : TypeAlias = str
FuncName_str : TypeAlias = str
Complexity_int : TypeAlias = int
LinesDuppedCount_int : TypeAlias = int

class FileMetricsDatabaseFacade:
    def get_function_complexities_for_one_file(self, file_id : str) -> dict[FuncName_str, Complexity_int]:
        query = db.session.query(Function.name, Complexity.value)
        query = query.join(Complexity, Function.id == Complexity.function_id)
        query = query.filter(Function.file_id == file_id)
        return FacadeUtilities.to_dict(query.all(), lambda row : (row[0], row[1]))
    
    def count_identifiable_entities_for_one_file(self, file_id : str) -> int:
        query = db.session.query(IdentifiableEntity)
        query = query.join(FileIdentifiableEntity, FileIdentifiableEntity.identifiable_entity_id == IdentifiableEntity.id)
        query = query.filter(FileIdentifiableEntity.file_id == file_id)
        return query.count()
    
    def get_code_duplications_for_one_file(self, file_id : str) -> list[tuple[LinesDuppedCount_int, CodeFragment]]: 
        query = db.session.query(Duplication.line_count, CodeFragment)
        query = query.join(Duplication, Duplication.code_fragment_id == CodeFragment.id)
        query = query.filter(Duplication.file_id == file_id)
        return FacadeUtilities.to_list(query.all(), lambda row : (row[0], row[1]))

    def get_function_complexities_for_many_files(self, file_id_list : list[str]) -> list[tuple[FileID_str, FuncName_str, Complexity_int]]: 
        query = db.session.query(Function.file_id, Function.name, Complexity.value)
        query = query.join(Complexity, Function.id == Complexity.function_id)
        query = query.filter(Function.file_id.in_(file_id_list))
        return FacadeUtilities.to_list(query.all(), lambda row : (row[0], row[1], row[2]))

    def count_identifiable_entities_for_many_files(self, file_id_list : list[str]) -> list[tuple[FileID_str, IdentifiableEntity]]:
        query = db.session.query(FileIdentifiableEntity.file_id ,IdentifiableEntity)
        query = query.join(FileIdentifiableEntity, FileIdentifiableEntity.identifiable_entity_id == IdentifiableEntity.id)
        query = query.filter(FileIdentifiableEntity.file_id.in_(file_id_list))
        return FacadeUtilities.to_list(query.all(), lambda row : (row[0], row[1]))
    
    def get_code_duplications_for_many_files(self, file_id_list : list[str]) -> list[tuple[FileID_str, LinesDuppedCount_int, CodeFragment]]:
        query = db.session.query(Duplication.file_id, Duplication.line_count, CodeFragment)
        query = query.join(Duplication, Duplication.code_fragment_id == CodeFragment.id)
        query = query.filter(Duplication.file_id.in_(file_id_list))
        return FacadeUtilities.to_list(query.all(), lambda row : (row[0], row[1], row[2]))