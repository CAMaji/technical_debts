from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests
from lizard import analyze_file
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
import os
from pydriller import Repository
from pydriller.git import Git
import tempfile
import subprocess

GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def run_query(query, variables=None):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    response.raise_for_status()
    return response.json()


def fetch_files(owner, repo, branch):
    repo_url = f"https://github.com/{owner}/{repo}.git"
    print(repo_url)
    print(branch)
    files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the repo to the temp directory
        subprocess.run(["git", "clone", "--branch", branch, "--single-branch", repo_url, tmpdir], check=True)
        repo_path = tmpdir
        for root, _, filenames in os.walk(repo_path):
            for filename in filenames:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                        rel_path = os.path.relpath(file_path, repo_path)
                        files.append((rel_path, code))
    return files