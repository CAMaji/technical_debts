from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta

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

from src.models import *
db.init_app(app)

import src.services.repository_service as repository_service
import src.services.branch_service as branch_service

import src.controllers.identifiable_entity_controller
import src.controllers.commit_controller
import src.controllers.metrics_controller
import src.controllers.repository_controller

import src.services.metrics_service as metrics_service


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


@app.route('/debt_evolution/<owner>/<name>/', methods=['GET'])
def debt_evolution(owner, name):
    
    """
        Return the debt evolution page for a repository with Plotly visualization.
    """
    try:
        repo = repository_service.get_repository_by_owner_and_name(owner, name)
        branches = branch_service.get_branches_by_repository_id(repo.id)

        # Calculate default dates: today and 30 days prior
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Format dates for the API (dd/mm/yyyy hh:mm)
        default_end_date = today.strftime('%d/%m/%Y 23:59')
        default_start_date = thirty_days_ago.strftime('%d/%m/%Y 00:00')

        # Get query parameters for date range and branch (with calculated defaults)
        start_date = request.args.get('start_date', default_start_date)
        end_date = request.args.get('end_date', default_end_date)
        branch_name = request.args.get('branch', 'main' if branches else None)
        
        # Find the selected branch or use the first one
        selected_branch = None
        if branch_name:
            selected_branch = next((b for b in branches if b.name == branch_name), None)
        if not selected_branch and branches:
            selected_branch = branches[0]
            
        debt_data = []
        if selected_branch:
            
            debt_data = metrics_service.calculate_debt_evolution(
                repo.id, 
                selected_branch.id, 
                start_date, 
                end_date
            )

        print("Print test:", debt_data)

        return render_template('debt_evolution.html', 
            repository=repo, 
            branches=branches, 
            selected_branch=selected_branch,
            debt_data=debt_data,
            start_date=start_date,
            end_date=end_date)
    except Exception as e:
        print(f"Error in debt_evolution: {str(e)}")
        return render_template('debt_evolution.html', 
            repository=None, 
            branches=None, 
            error=str(e))

#import src.services.identifiable_entity_service as identifiable_entity_service
#with app.app_context():
#    print('dropping...')
#    db.drop_all()
#    db.reflect()
#    db.create_all()
#    identifiable_entity_service.create_identifiable_entity("todo")
#    identifiable_entity_service.create_identifiable_entity("fixme")
#    db.session.commit()