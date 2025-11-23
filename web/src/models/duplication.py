import uuid
from src.models import db
from src.models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)
from src.utilities.value_range import ValueRange
from src.utilities.json_encoder import JsonEncoder

class Duplication(ModelMixin, db.Model): 
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

    def __init__(self, code_fragment_id : str, file_id : str, line_count : int, line_domain : ValueRange, column_domain : ValueRange): 
        self.id = str(uuid.uuid4())
        self.code_fragment_id = code_fragment_id
        self.file_id = file_id
        self.line_count = line_count
        self.from_line = line_domain.From
        self.to_line = line_domain.To
        self.from_column = column_domain.From
        self.to_column = column_domain.To
        return
    
    def lines(self) -> ValueRange: 
        return ValueRange(self.from_line, self.to_line)
    
    def columns(self) -> ValueRange: 
        return ValueRange(self.from_column, self.to_column)
