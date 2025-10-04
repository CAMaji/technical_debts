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
from datetime import datetime

import services.repository_service as repository_service


def fetch_files(owner, name, branch, commit_sha):
    repo_url = f"https://github.com/{owner}/{name}.git"
    files = []

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone only the branch
        subprocess.run(
            ["git", "clone", "--branch", branch, "--single-branch", repo_url, tmpdir],
            check=True
        )

        # Checkout the specific commit
        subprocess.run(["git", "-C", tmpdir, "checkout", commit_sha], check=True)

        repo_path = tmpdir
        for root, _, filenames in os.walk(repo_path):
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        rel_path = os.path.relpath(file_path, repo_path)
                        files.append((rel_path, code))

    return files

def fetch_branches(owner, name):
    try:
        repo_url = repository_service.get_repository_url_by_owner_and_name(owner, name)
        stdout = subprocess.check_output(['git', 'ls-remote', '--heads', repo_url], stderr=subprocess.STDOUT)
        out = stdout.decode()
        branches = [line.split()[1].replace("refs/heads/", "") for line in out.splitlines()]

        return branches
    except subprocess.CalledProcessError as e:
        print(f"Error fetching branches: {e.output.decode()}")
        return []


def get_closest_commit(repo_url: str, branch: str, date_str: str) -> tuple[str, str]:
    """
    Get the commit SHA and date from `branch` of `repo_url` closest before `date_str`.

    Args:
        repo_url (str): Git repository URL
        branch (str): Branch name
        date_str (str): Date string in "dd/mm/yyyy hh:mm" format

    Returns:
        tuple[str, str]: (commit_sha, commit_date in "dd/mm/yyyy hh:mm")
    """
    # Parse input date into ISO format for git
    dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
    git_date = dt.isoformat(" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone only the branch (no checkout to save time)
        subprocess.run(
            ["git", "clone", "--branch", branch, "--single-branch", "--no-checkout", repo_url, tmpdir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Find commit before that date
        commit_sha = subprocess.check_output(
            ["git", "-C", tmpdir, "rev-list", "-n", "1", f"--before={git_date}", branch],
            text=True
        ).strip()

        if not commit_sha:
            return None, None

        # Get commit date (ISO 8601)
        commit_date_iso = subprocess.check_output(
            ["git", "-C", tmpdir, "show", "-s", "--format=%cI", commit_sha],
            text=True
        ).strip()

        # Convert ISO 8601 → dd/mm/yyyy hh:mm
        commit_dt = datetime.fromisoformat(commit_date_iso.replace("Z", "+00:00"))
        commit_date = commit_dt.strftime("%d/%m/%Y %H:%M")

        return commit_sha, commit_date