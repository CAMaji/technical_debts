from src.models import db
from src.models.model import *

from src.models.duplication import Duplication
from src.utilities.facade_utilities import FacadeUtilities
from src.utilities.smart_list_iterator import SmartListIterator
from src.utilities.smart_dict_iterator import SmartDictIterator
from sqlalchemy.orm import Query
from sqlalchemy.engine import Row
from sqlalchemy import func

class FileMetricsDatabaseFacade:

    def get_average_complexities(self, files : list[File]) -> dict[ID, float]: 
        """
        Returns a dict that contains the average complexity for each file\n
        in provided list.\n
        `Dict[FileID, AverageComplexity]`
        """
        iterator = SmartListIterator[File, ID](files, lambda file: file.id)
        query : Query = db.session.query(Function.file_id, 
                                         func.avg(Complexity.value))
        query : Query = query.join(Complexity, Function.id == Complexity.function_id)
        query : Query = query.filter(Function.file_id.in_(iterator))
        query : Query = query.group_by(Function.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( ID(row[0]), float(row[1]) ) )
    
    def get_identifiable_entities_count(self, files : list[File]) -> dict[ID, float]:
        """
        Returns a dict that contains the nb of IdentifiableEntity for each\n
        file in provided list.\n
        `Dict[FileID, NbOfIdentifiableEntity]`
        """
        iterator = SmartListIterator[File, ID](files, lambda file: file.id)
        query : Query = db.session.query(FileIdentifiableEntity.file_id, 
                                         func.count(FileIdentifiableEntity.identifiable_entity_id))
        query : Query = query.filter(FileIdentifiableEntity.file_id.in_(iterator))
        query : Query = query.group_by(FileIdentifiableEntity.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( ID(row[0]), float(row[1]) ) )

    def get_duplications_metrics(self, files : list[File]) -> dict[ID, tuple[float, float]]:
        """
        Returns a dict that contains the number of CodeFragment and the sum of duplicated lines\n
        for each file in provided list. \n
        `Dict[FileID, tuple[CodeFragmentCount, SumOfDuplicatedLines]]`
        """
        iterator = SmartListIterator[File, ID](files, lambda file: file.id)
        query : Query = db.session.query(Duplication.file_id, 
                                         func.count(Duplication.code_fragment_id), 
                                         func.sum(Duplication.line_count))
        query : Query = query.filter(Duplication.file_id.in_(iterator))
        query : Query = query.group_by(Duplication.file_id)
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_dict(row_list, lambda row: ( ID(row[0]), ( float(row[1]), float(row[2]) )) )
    
    def get_functions_complexity(self, files : list[File]) -> dict[ID, list[tuple[str, float]]]:
        """
        Returns a dict that contains the list of function names and their complexity for\n
        for each file in provided list. \n
        `Dict[FileID, list[tuple[FunctionName, FunctionComplexity]]]`
        """
        iterator = SmartListIterator[File, ID](files, lambda file: file.id)
        query : Query = db.session.query(Function.file_id, 
                                         Function.name,
                                         Complexity.value)
        query : Query = query.join(Complexity, Function.id == Complexity.function_id)
        query : Query = query.filter(Function.file_id.in_(iterator))
        row_list : list[Row] = query.all()
        return FacadeUtilities.to_list_dict(row_list, lambda row: ( ID(row[0]), ( str(row[1]), float(row[2]) )) )