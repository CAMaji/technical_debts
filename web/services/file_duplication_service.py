import uuid
from app import db
from models.model import *
import services.file_service as file_service
import json

# Creates and commits a FileDuplication row.
def file_duplication_create(file_id, duplication_id): 
    file_duplication = FileDuplication(
        id = str(uuid.uuid4()),
        file_id = file_id,
        duplication_id = duplication_id
    )

    db.session.add(file_duplication)
    db.session.commit()

    return file_duplication 

# Obtains all file-duplication objects for a given file id
def file_duplication_get_from_file(file_id):
    return db.session.query(FileDuplication).filter_by(file_id=file_id).all()
        
# Obtains a JSON representation of a FileDuplication object
def file_duplication_to_json(file : File, file_duplications : list[FileDuplication]): 
    duplication_id_list = []
    for fd in file_duplications: 
        duplication_id_list.append(fd.duplication_id)

    return {
        "filename": file.name,
        "count": len(file_duplications),
        "duplication_ids": json.dumps(duplication_id_list)
    }

# Obtains a json object of duplications for each files in a commit
def file_duplication_get_json_from_commit(commit : Commit): 
    json_list = []
    files : list[File] = file_service.get_files_by_commit_id(commit.id)
    duplications : set = set()

    for f in files: 
        file_duplications : list[FileDuplication] = file_duplication_get_from_file(f.id)

        # On ajoute au set le ID de duplication
        # Le nombre de ID ajouté au set = le nombre
        # de duplications pour le commit sélectionné
        for fd in file_duplications: 
            duplications.add(fd.duplication_id)

        json_fd = file_duplication_to_json(f, file_duplications)
        json_list.append(json_fd)

    # copie le contenu du set vers une liste
    duplication_list : list = []
    for d in duplications:
        duplication_list.append(d)

    result = {
        "file_duplications": json.dumps(json_list),
        "unique_duplication_ids": json.dumps(duplication_list)
    }

    print(result)

    return result