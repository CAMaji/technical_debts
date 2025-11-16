from models.model import db, Complexity, Function, IdentifiableEntity, FileIdentifiableEntity
from models.code_duplication import CodeDuplicationModel
from models.file_code_duplication import FileCodeDuplicationModel

class FileStatisticsDatabaseFacade:
    # list of tuple
    # tuple[1]: function name (str)
    # tuple[2]: complexity of function (int)
    def get_function_complexities_for_one_file(self, file_id : str) -> list[tuple[str, int]]:
        query = db.session.query(Function.name, Complexity.value)
        query = query.join(Complexity, Function.id == Complexity.function_id)
        query = query.filter(Function.file_id == file_id)
        return query.all()
    
    def get_identifiable_entities_for_one_file(self, file_id : str) -> list[IdentifiableEntity]:
        query = db.session.query(IdentifiableEntity)
        query = query.join(FileIdentifiableEntity, FileIdentifiableEntity.identifiable_entity_id == IdentifiableEntity.id)
        query = query.filter(FileIdentifiableEntity.file_id == file_id)
        return query.all()
    
    # list of tuple
    # tuple[0]: line count (int)
    # tuple[1]: CodeDuplicationModel
    def get_code_duplications_for_one_file(self, file_id : str) -> list[tuple[int, CodeDuplicationModel]]: 
        query = db.session.query(FileCodeDuplicationModel.line_count, CodeDuplicationModel)
        query = query.join(FileCodeDuplicationModel, FileCodeDuplicationModel.code_duplication_id == CodeDuplicationModel.id)
        query = query.filter(FileCodeDuplicationModel.file_id == file_id)
        return query.all()
    
    # list of tuple
    # tuple[0]: file id (str)
    # tuple[1]: function name (str)
    # tuple[2]: complexity of function (int)
    def get_function_complexity_for_many_files(self, file_id_list : list[str]) -> list[tuple[str, str, int]]: 
        query = db.session.query(Function.file_id, Function.name, Complexity.value)
        query = query.join(Complexity, Function.id == Complexity.function_id)
        query = query.filter(Function.file_id.in_(file_id_list))
        return query.all()
    
    # list of tuple
    # tuple[0]: file id (str)
    # tuple[1]: IdentifiableEntity
    def get_identifiable_entities_for_many_files(self, file_id_list : list[str]) -> list[tuple[str, IdentifiableEntity]]:
        query = db.session.query(FileIdentifiableEntity.file_id ,IdentifiableEntity)
        query = query.join(FileIdentifiableEntity, FileIdentifiableEntity.identifiable_entity_id == IdentifiableEntity.id)
        query = query.filter(FileIdentifiableEntity.file_id.in_(file_id_list))
        return query.all()
    
    # list of tuple
    # tuple[0]: file id (str)
    # tuple[1]: line count (int)
    # tuple[2]: CodeDuplicationModel
    def get_code_duplications_for_many_files(self, file_id_list : list[str]) -> list[tuple[str, int, CodeDuplicationModel]]:
        query = db.session.query(FileCodeDuplicationModel.file_id, FileCodeDuplicationModel.line_count, CodeDuplicationModel)
        query = query.join(FileCodeDuplicationModel, FileCodeDuplicationModel.code_duplication_id == CodeDuplicationModel.id)
        query = query.filter(FileCodeDuplicationModel.file_id.in_(file_id_list))
        return query.all()