from src.models.model import File
from src.models.duplication import Duplication
from src.utilities.custom_json_encoder import CustomJsonEncoder

class CodeFragmentReferent(CustomJsonEncoder): 
    file: File
    duplication: Duplication

    def __init__(self, file : File, duplication : Duplication):
        self.file = file
        self.duplication = duplication

    def encode(self):
        return {
            "file": self.file.encode(),
            "duplication": self.duplication.encode()
        }