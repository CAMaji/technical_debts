from models.model import *
import json

# contains the template sql query that calculates the priority of a file
# for a given commit. 
prioritisation_query = ""

def get_file_prioritisation_for_commit(commit : Commit): 
    global prioritisation_query
    if prioritisation_query == "":
        with open("/app/sql/fp2.sql") as f:
            prioritisation_query = f.read()
    
    # copies the query and replace the wildcard by the commit id
    commit_specific_query = prioritisation_query.replace("@", commit.id)
    
    db = get_db()
    result = db.session.execute(commit_specific_query)
    json_list = []

    # source: https://stackoverflow.com/a/22084672 
    for r in result: 
        score : float = float(r['score'])
        filename : str = str(r['file_name'])
        json_list.append({
            "filename": filename,
            "score": score 
        })
     
    return json.dumps(json_list)

