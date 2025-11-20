from src.utilities.custom_json_encoder import CustomJsonEncoder

class FileMetrics(CustomJsonEncoder):
    file_id : str
    file_name : str
    avg_complexity : float
    #complexities: dict[str, int]
    identifiable_entities : int
    duplication_count : int
    lines_duplicated : int

    def __init__(self, file_id : str, file_name : str, ac : float, ie : int, dc : int, ld : int): 
        self.file_id = file_id
        self.file_name = file_name
        self.avg_complexity = ac
        #self.complexities = complexities
        self.identifiable_entities = ie
        self.duplication_count = dc
        self.lines_duplicated = ld

    def encode(self):
        return {
            "file_id" : self.file_id,
            "file_name": self.file_name,
            "avg_complexity": self.avg_complexity,
            #"complexities": CustomJsonEncoder.breakdown(self.complexities),
            "identifiable_entities": self.identifiable_entities,
            "duplication_count": self.duplication_count,
            "lines_duplicated": self.duplication_count
        }