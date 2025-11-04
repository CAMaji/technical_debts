import uuid
from app import db
from models.model import *

# Creates and commits a Duplication row.
def duplication_create(text : str): 
    duplication = Duplication(
        id = str(uuid.uuid4()),
        text = text
    )

    db.session.add(duplication)
    db.session.commit()

    return duplication

# Obtains a duplication object from id 
def duplication_get_from_id(id):
    return db.session.query(Duplication).filter_by(duplication_id=id).first()
