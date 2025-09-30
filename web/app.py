from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from lizard import analyze_file
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from models import *
import services.repo_service as repo_service


# FLASK EXAMPLE
@app.route('/', methods=['GET'])
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    post = Post(text)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))


# Complexity analysis
@app.route("/complexity/<owner>/<repo>/", defaults={"branch": None})
@app.route("/complexity/<owner>/<repo>/<branch>")
def complexity(owner, repo, branch):
    # Use "main" as default if branch is not provided
    branch = branch or "main:"
    files = repo_service.fetch_files(owner, repo, branch)
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

if __name__ == '__main__':
    app.run()
