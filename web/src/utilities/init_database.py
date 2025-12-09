"""
Database initialization - creates tables and seeds default identifiable entities
"""
from src.models import db
from src.models.model import IdentifiableEntity
import uuid


def init_database():
    """Initialize database tables and seed with default data"""
    print("Creating database tables...")
    db.create_all()
    
    print("Seeding default identifiable entities...")
    
    # Check if entities already exist
    existing_todo = IdentifiableEntity.query.filter_by(name='TODO').first()
    existing_fixme = IdentifiableEntity.query.filter_by(name='FIXME').first()
    
    if not existing_todo:
        todo_entity = IdentifiableEntity(id=str(uuid.uuid4()),name='TODO')
        db.session.add(todo_entity)
        print("  ✓ Added TODO entity")
    else:
        print("  - TODO entity already exists")
    
    if not existing_fixme:
        fixme_entity = IdentifiableEntity(id=str(uuid.uuid4()),name='FIXME')
        db.session.add(fixme_entity)
        print("  ✓ Added FIXME entity")
    else:
        print("  - FIXME entity already exists")
    
    db.session.commit()
    print("Database initialization complete!")


if __name__ == "__main__":
    from src.app import app
    
    with app.app_context():
        init_database()
