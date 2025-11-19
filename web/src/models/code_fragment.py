import uuid
from src.models.model import db
from src.models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)
from src.utilities.custom_json_encoder import CustomJsonEncoder

class CodeFragment(ModelMixin, db.Model, CustomJsonEncoder): 
    __tablename__ = "code_fragment"
    # PK
    id = Column(String(36), primary_key = True)

    # Columns
    text = Column(Text)
    line_count = Column(Integer)

    def __init__(self, text, line_count=0):
        self.id = str(uuid.uuid4())
        self.text = text
        self.line_count = line_count
        return
    
    def encode(self): 
        return {
            "id": self.id,
            "text": self.text,
            "line_count": self.line_count
        }