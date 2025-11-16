from models.model import *
from database.file_statistics_db_facade import FileStatisticsDatabaseFacade
from database.file_statistics_db_facade import FuncName_str, Complexity_int
from utilities.custom_json_encoder import CustomJsonEncoderInterface

class FileCodeDuplicationStats(CustomJsonEncoderInterface): 
    duplication_count : int
    lines_duplicated : int

    def __init__(self, duplication_count : int, lines_duplicated : int):
        self.duplication_count = duplication_count
        self.lines_duplicated = lines_duplicated

    def encode(self):
        return {
            "duplication_count": self.duplication_count,
            "lines_duplicated": self.lines_duplicated
        }
    
class FileTechDebtStats(CustomJsonEncoderInterface):
    complexity: float
    identifiable_entities : float
    duplication_count : float
    lines_duplicated : float

    def __init__(self, cw : float, ie : float, dc : float, ld : float): 
        self.complexity = cw
        self.identifiable_entities = ie
        self.duplication_count = dc
        self.lines_duplicated = ld

    def encode(self): 
        return {
            "complexity_weight": self.complexity,
            "identifiable_entities_weight": self.identifiable_entities,
            "duplication_count_weight": self.duplication_count,
            "lines_duplicated": self.lines_duplicated
        }

class FileStatisticsService: 
    _facade : FileStatisticsDatabaseFacade

    def __init__(self, facade : FileStatisticsDatabaseFacade): 
        self._facade = facade
        return

    def get_function_complexities_for_one_file(self, file_id : str) -> dict[FuncName_str, Complexity_int]:
        rows = self._facade.get_function_complexities_for_one_file(file_id)
        function_complexities : dict[str, int] = {}
        for r in rows: 
            function_complexities[r[0]] = r[1]
        return function_complexities

    def count_identifiable_identities_for_one_file(self, file_id : str) -> int:
        return self._facade.count_identifiable_entities_for_one_file(file_id)

    def get_complexity_average_for_one_file(self, file_id : str) -> float:
        function_complexities = self.get_function_complexities_for_one_file(file_id)
        count = len(function_complexities)
        
        if count == 0: # prevents a divison by zero exception
            return 0

        sum : float = 0.0
        for k in function_complexities: 
            sum += function_complexities[k]

        return sum / count
        
    def get_code_duplications_stats_for_one_file(self, file_id : str) -> FileCodeDuplicationStats:
        code_duplications = self._facade.get_code_duplications_for_one_file(file_id)
        duplication_count : int = len(code_duplications)
        lines_duplicated : int = 0

        for cd in code_duplications:
            lines_duplicated += cd[0]

        return FileCodeDuplicationStats(duplication_count, lines_duplicated)

    def get_tech_debt_stats_for_one_file(self, file_id : str) -> FileTechDebtStats:
        complexity_avg = self.get_complexity_average_for_one_file(file_id)
        identifiable_entities_count = self.count_identifiable_identities_for_one_file(file_id)
        duplication_stats = self.get_code_duplications_stats_for_one_file(file_id)

        return FileTechDebtStats(
            complexity_avg, 
            identifiable_entities_count, 
            duplication_stats.duplication_count, 
            duplication_stats.lines_duplicated
        )
    
    
