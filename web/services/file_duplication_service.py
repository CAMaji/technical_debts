import uuid
from app import db
from models import *

# Creates and commits a FileDuplication row.
def file_duplication_create(file_id : str, duplication_id : int): 
    file_duplication = FileDuplication(
        id = str(uuid.uuid4()),
        file_id = file_id,
        duplication_id = duplication_id
    )

    db.session.add(file_duplication)
    db.session.commit()

    return file_duplication

