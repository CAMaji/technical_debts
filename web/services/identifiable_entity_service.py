import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from app import db
from models import *

def create_identifiable_entity(name):
    indentifiable_entity = IdentifiableEntity(
        id = str(uuid.uuid4()),
        name = name,
        
    )

    db.session.add(indentifiable_entity)
    db.session.commit()

    return indentifiable_entity


def get_identifiable_entity_by_name(name):
    return db.session.query(IdentifiableEntity).filter_by(name=name).first()


def get_identifiable_entity_by_name_and_file(name: str, file_id: str):
    return (
        db.session.query(IdentifiableEntity)
        .filter(IdentifiableEntity.name == name))
