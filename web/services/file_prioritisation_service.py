from models.model import *
import json

# contains the sql query that calculates the priority of a file
# for a given commit. 
prioritisation_query = None

def get_file_prioritisation_for_commit(commit : Commit): 
    if prioritisation_query == None:
        with open("./web/sql/file-prioritisation.sql") as f:
            prioritisation_query = f.read()

    db = get_db()
    result = db.session.execute(prioritisation_query)
    json_list = []

    # source: https://stackoverflow.com/a/22084672 
    for r in result: 
        json_list.append({
            "filename": r['file_name'],
            "score": r['score']
        })
    
    return json.dumps(json_list)

