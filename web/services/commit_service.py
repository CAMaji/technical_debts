import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from models import db
from models.model import *


def create_commit(commit_sha, commit_date, author, message, branch_id):
    commit = Commit(
        id = str(uuid.uuid4()),
        sha = commit_sha,
        date = commit_date,
        author = author,
        message = message,
        branch_id = branch_id,
    )

    db.session.add(commit)
    db.session.commit()

    return commit


def get_commit_by_sha(commit_sha):
    return db.session.query(Commit).filter_by(sha=commit_sha).first()


def get_commits_by_branch_id(branch_id):
    commits = Commit.query.filter_by(branch_id=branch_id).all()

    return [commit.as_dict() for commit in commits]


def get_commits_by_branch_name(branch_name):
    branch = Branch.query.filter_by(branch_name=branch_name).first()

    commits = Commit.query.filter_by(branch_id=branch.id).all()

    return [commit.as_dict() for commit in commits]