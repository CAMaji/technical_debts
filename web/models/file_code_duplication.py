import uuid
from models.model import db
from models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)

class FileCodeDuplicationModel(ModelMixin, db.Model): 
    __tablename__ = "file_code_duplication"
    # PK
    id = Column(String(36), primary_key = True)
    # FK
    code_duplication_id = Column(String(36), ForeignKey("code_duplication.id"))
    file_id = Column(String(36), ForeignKey("file.id"))
    # Columns
    line_count = Column(Integer)

    def __init__(self, code_duplication_id : str, file_id : str, line_count : int): 
        self.id = str(uuid.uuid4())
        self.code_duplication_id = code_duplication_id
        self.file_id = file_id
        self.line_count = line_count
        return