from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from models import *

import services.repository_service as repository_service
import services.branch_service as branch_service


import controllers.metrics_controller
import controllers.repository_controller

@app.route('/', methods=['GET'])
def index():
    """
        Landing page
    """
    try:
        repositories = repository_service.get_all_repositories()
    except Exception:
        repositories = []

    return render_template('index.html', repositories=repositories)


@app.route('/dashboard/<owner>/<name>/', methods=['GET'])
def dashboard(owner, name):
    """
        Return the dashboard for a repository. Repo needs to be created first.
    """
    try:
        repo = repository_service.get_repository_by_owner_and_name(owner, name)
        branches = branch_service.get_branches_by_repository_id(repo.id)

        return render_template('dashboard.html', repository=repo, branches=branches)
    except Exception as e:
        print(str(e))
        return render_template('dashboard.html', repository=None, branches=None)


if __name__ == '__main__':
    app.run()
