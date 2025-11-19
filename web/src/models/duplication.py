import uuid
from src.models.model import db
from src.models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)
from src.utilities.value_range import ValueRange
from src.utilities.custom_json_encoder import CustomJsonEncoder

class Duplication(ModelMixin, db.Model, CustomJsonEncoder): 
    __tablename__ = "duplication"
    # PK
    id = Column(String(36), primary_key = True)
    
    # FK
    code_fragment_id = Column(String(36), ForeignKey("code_fragment.id"))
    file_id = Column(String(36), ForeignKey("file.id"))

    # Columns
    line_count = Column(Integer)
    from_line = Column(Integer)
    to_line = Column(Integer)
    from_column = Column(Integer)
    to_column = Column(Integer)

    def __init__(self, code_fragment_id : str, file_id : str, line_count : int, line_domain : ValueRange[int] = None, column_domain : ValueRange[int] = None): 
        self.id = str(uuid.uuid4())
        self.code_fragment_id = code_fragment_id
        self.file_id = file_id
        self.line_count = line_count
        if line_domain != None:
            self.from_line = line_domain.From
            self.to_line = line_domain.To
        else: 
            self.from_line = 0
            self.to_line = 0
        if column_domain != None:
            self.from_column = column_domain.From
            self.to_column = column_domain.To
        else:
            self.from_column = 0
            self.to_column = 0
        return
    
    def encode(self):
        return {
            "id": self.id,
            "code_fragment": self.code_fragment_id,
            "file_id": self.file_id,
            "line_count": self.line_count,
            "lines": {"from": self.from_line, "to": self.to_line},
            "columns": {"from": self.from_column, "to": self.to_column}
        }
