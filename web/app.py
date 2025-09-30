from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from lizard import analyze_file
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from models import *

@app.route('/', methods=['GET'])
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    print('here')
    return render_template('index.html', posts=posts)

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    post = Post(text)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))

GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def run_query(query, variables=None):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_files(owner, repo, expression="proof_of_concept:", path=""):
    query = """
    query($owner: String!, $name: String!, $expression: String!) {
      repository(owner: $owner, name: $name) {
        object(expression: $expression) {
          ... on Tree {
            entries {
              name
              type
              object {
                ... on Blob {
                  text
                }
              }
            }
          }
        }
      }
    }
    """
    result = run_query(query, {"owner": owner, "name": repo, "expression": expression + path})
    repo_obj = result["data"]["repository"]["object"]
    if not repo_obj or "entries" not in repo_obj:
        return []
    entries = repo_obj["entries"]
    files = []
    for entry in entries:
        if entry["type"] == "blob" and entry["name"].endswith(".py"):
            files.append((path + entry["name"], entry["object"]["text"]))
        elif entry["type"] == "tree":
            # Recursively fetch files in subfolders
            files.extend(fetch_files(owner, repo, expression, path + entry["name"] + "/"))
    return files

@app.route("/complexity/<owner>/<repo>")
def complexity(owner, repo):
    files = fetch_files(owner, repo)
    results = []

    for filename, code in files:
        analysis = analyze_file.analyze_source_code(filename, code)
        for func in analysis.function_list:
            results.append({
                "file": filename,
                "function": func.name,
                "start_line": func.start_line,
                "cyclomatic_complexity": func.cyclomatic_complexity
            })
    
    

    return jsonify(results)

def complicated_function(x, y):
    result = 0
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                result += i
            else:
                if y > 0:
                    result -= y
                else:
                    for j in range(abs(y)):
                        if j % 3 == 0:
                            result += j
                        else:
                            result -= j
    elif x == 0:
        if y == 0:
            result = 42
        else:
            result = -42
    else:
        while x < 0:
            result += x
            x += 1
    return result

if __name__ == '__main__':
    app.run()
