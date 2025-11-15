import uuid
import json
from models.model import db
from models.model import ModelMixin
from sqlalchemy import (Column, String, Integer, Float, Text, ForeignKey, DateTime)
from utilities.custom_json_encoder import *

class CodeDuplicationModel(ModelMixin, db.Model, CustomJsonEncoderInterface): 
    __tablename__ = "code_duplication"
    # PK
    id = Column(String(36), primary_key = True)
    # Columns
    text = Column(Text)

    def __init__(self, text):
        self.id = str(uuid.uuid4())
        self.text = text
        return
    
    def encode(self):
        return {
            "id": self.id, 
            "text": self.text
        }