from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is created to avoid circular imports
from models.model import (
    Repository, Branch, Commit, File, Function,
    IdentifiableEntity, FileIdentifiableIdentitty,
    Complexity, Coverage, Size, Tests,
    FileTestCoverage
)

__all__ = [
    'db',
    'Repository', 'Branch', 'Commit', 'File', 'Function',
    'IdentifiableEntity', 'FileIdentifiableIdentitty',
    'Complexity', 'Coverage', 'Size', 'Tests',
    'FileTestCoverage'
]