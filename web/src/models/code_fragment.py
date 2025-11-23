import uuid
from src.models.model import db
from src.models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)

class CodeFragment(ModelMixin, db.Model): 
    __tablename__ = "code_fragment"
    # PK
    id = Column(String(36), primary_key = True)

    # Columns
    text = Column(Text)
    line_count = Column(Integer)

    def __init__(self, text: str, line_count: int):
        self.id = str(uuid.uuid4())
        self.text = text
        self.line_count = line_count
        return