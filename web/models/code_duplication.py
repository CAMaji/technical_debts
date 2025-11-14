import uuid
import json
from models.model import db
from models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)

class CodeDuplicationModel(ModelMixin, db.Model): 
    __tablename__ = "code_duplication"
    # PK
    id = Column(String(36), primary_key = True)
    # Columns
    text = Column(Text)

    def __init__(self, text):
        self.id = str(uuid.uuid4())
        self.text = text
        return