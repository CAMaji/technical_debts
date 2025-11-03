from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret!"

# Database configuration
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'postgres')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_ENABLE_POOL_PRE_PING'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import *
db.init_app(app)

import services.repository_service as repository_service
import services.branch_service as branch_service

import controllers.metrics_controller
import controllers.repository_controller
import controllers.commit_controller


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


# with app.app_context():
#     print('dropping...')
#     db.reflect()
#     db.drop_all()
#     db.create_all()
#     db.session.commit()