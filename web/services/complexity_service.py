import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from app import db
from models import *


def create_complexity(value, function_id):
    complexity = Complexity(
        id = str(uuid.uuid4()),
        value = value,
        function_id = function_id,
    )

    db.session.add(complexity)
    db.session.commit()

    return complexity