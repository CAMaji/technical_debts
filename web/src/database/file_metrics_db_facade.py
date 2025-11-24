from src.models import db
from src.models.model import *

from src.models.duplication import Duplication
from src.utilities.facade_utilities import FacadeUtilities
from src.utilities.smart_list_iterator import SmartListIterator
from src.utilities.smart_dict_iterator import SmartDictIterator
from src.utilities.value_range import ValueRange
from typing import TypeAlias
from sqlalchemy.orm import Query
from sqlalchemy.engine import Row
from sqlalchemy import func

class FileMetricsDatabaseFacade:

    def get_average_complexities(self, files : list[File]) -> dict[str, float]: 
        iterator = SmartListIterator[File, str](files, lambda file: file.id)
        query : Query = db.session.query(Function.file_id, func.avg(Complexity.value))
        query : Query = query.join(Complexity, Function.id == Complexity.function_id)
        query : Query = query.filter(Function.file_id.in_(iterator))
        query : Query = query.group_by(Function.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( str(row[0]), float(row[1]) ) )
    
    def get_identifiable_entities_count(self, files : list[File]) -> dict[str, float]:
        iterator = SmartListIterator[File, str](files, lambda file: file.id)
        query : Query = db.session.query(FileIdentifiableEntity.file_id, func.count(FileIdentifiableEntity.identifiable_entity_id))
        query : Query = query.filter(FileIdentifiableEntity.file_id.in_(iterator))
        query : Query = query.group_by(FileIdentifiableEntity.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( str(row[0]), float(row[1]) ) )

    def get_duplications_metrics(self, files : list[File]) -> dict[str, tuple[float, float]]:
        iterator = SmartListIterator[File, str](files, lambda file: file.id)
        query : Query = db.session.query(Duplication.file_id, 
                                         func.count(Duplication.code_fragment_id), 
                                         func.sum(Duplication.line_count))
        query : Query = query.filter(Duplication.file_id.in_(iterator))
        query : Query = query.group_by(Duplication.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( str(row[0]), ( float(row[1]), float(row[2]) )) )
    
    def get_files_per_duplication(self, files : list[File]) -> dict[str, list[tuple[str, float]]]:
        iterator = SmartListIterator[File, str](files, lambda file: file.id)
        query : Query = db.session.query(Duplication.code_fragment_id, 
                                         Duplication.file_id, 
                                         Duplication.line_count)
        query : Query = query.filter(Duplication.file_id.in_(iterator))
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_list_dict(row_list, lambda row: ( str(row[0]), ( str(row[1]), float(row[2]) )) )
    
    def get_functions_complexity(self, files : list[File]) -> dict[str, list[tuple[str, float]]]:
        iterator = SmartListIterator[File, str](files, lambda file: file.id)
        query : Query = db.session.query(Function.file_id, 
                                         Function.name,
                                         Complexity.value)
        query : Query = query.join(Complexity, Function.id == Complexity.function_id)
        query : Query = query.filter(Function.file_id.in_(iterator))
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_list_dict(row_list, lambda row: ( str(row[0]), ( str(row[1]), float(row[2]) )) )