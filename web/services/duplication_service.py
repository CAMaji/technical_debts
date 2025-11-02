import uuid
from app import db
from models import *

# Creates and commits a Duplication row.
def duplication_create(text : str): 
    duplication = Duplication(
        id = str(uuid.uuid4()),
        text = text
    )

    db.session.add(duplication)
    db.session.commit()

    return duplication