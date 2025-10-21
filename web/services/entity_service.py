from app import db
from ...web.models import IdentifiableEntity, FileEntities
import uuid

def get_or_create_entity(entity_name):
    """Get existing entity or create a new one"""
    entity = IdentifiableEntity.query.filter_by(name=entity_name).first()
    if not entity:
        entity = IdentifiableEntity(
            id=str(uuid.uuid4()),
            name=entity_name
        )
        db.session.add(entity)
        db.session.commit()
    return entity

def create_file_entity(file_id, entity_id, line_position):
    """Create file entity relationship"""
    file_entity = FileEntities(
        id=str(uuid.uuid4()),
        file_id=file_id,
        entity_id=entity_id,
        line_position=line_position
    )
    db.session.add(file_entity)
    db.session.commit()
    return file_entity

def get_file_entities_by_file_id(file_id):
    """Get all entities for a file"""
    return FileEntities.query.filter_by(file_id=file_id).all()