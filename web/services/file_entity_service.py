import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from models import db
from models.model import *

def create_file_entity(name, line_position, file_id):
    file_entity = FileEntities(
        id = str(uuid.uuid4()),
        name = name,
        line_position = line_position,
        file_id = file_id,
    )

    db.session.add(file_entity)
    db.session.commit()

    return file_entity


def get_file_entity_by_name(name):
    return db.session.query(FileEntities).filter_by(name=name).first()


def get_file_entity_by_name_and_file(name: str, file_id: str, line_position: int):
    return (
        db.session.query(FileEntities)
        .filter(FileEntities.name == name, FileEntities.file_id == file_id, FileEntities.line_position == line_position)
        .first()
    )
