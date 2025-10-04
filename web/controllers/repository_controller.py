from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
from app import app
import requests
from flask_sqlalchemy import SQLAlchemy

import services.repository_service as repository_service
import services.branch_service as branch_service


@app.route('/create_repository', methods=['POST'])
def create_repository():
    """
        Create a new repository

        :param owner: Github username of the repository owner
        :param repo: Github repository name
    """

    owner = request.form.get('owner')
    name = request.form.get('name')

    # Create a repo
    repo = repository_service.create_repository(owner, name)

    # Create objects for all the items
    branch_service.create_branches_from_repository(repo.id)

    # Redirect to the repository dashboard after creating it
    return redirect(url_for('dashboard', owner=owner, name=name))