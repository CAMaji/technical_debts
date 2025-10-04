import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from app import db
from models import *


def create_commit(commit_sha, commit_date, branch_id):
    commit = Commit(
        id = str(uuid.uuid4()),
        sha = commit_sha,
        date = commit_date,
        branch_id = branch_id,
    )

    db.session.add(commit)
    db.session.commit()

    return commit


def get_commit_by_sha(commit_sha):
    return db.session.query(Commit).filter_by(sha=commit_sha).first()