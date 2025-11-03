import uuid
from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
import requests

from models import db
from models.model import *

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
    

def search_identifable_identity(file, identifiable_identity):
    """
    Search for a string sequence in file content.
    
    Args:
        file: File content as string (from Lizard or other source)
        identifiable_identity: String sequence to search for
    
    Returns:
        List of Finding objects with line numbers where the string was found
    """
    findings = []
    
    lines = file.splitlines(keepends=True)
    
    # Search each line for the identifiable_identity
    for line_num, line in enumerate(lines, start=1):
        if identifiable_identity in line:
            findings.append({
                "name": identifiable_identity,
                "start_line": line_num
            })
    
    return findings