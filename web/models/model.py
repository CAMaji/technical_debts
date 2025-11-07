from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, DateTime
)
from sqlalchemy import inspect
from datetime import datetime
import enum
from models import db

class ModelMixin:
    def as_dict(self, include_relationships: bool = True):
        mapper = inspect(self.__class__)
        result = {}
        for column in mapper.columns:
            key = column.key
            val = getattr(self, key)
            if isinstance(val, enum.Enum):
                result[key] = val.value
            elif isinstance(val, datetime):
                result[key] = val.isoformat()
            else:
                result[key] = val
        if include_relationships:
            for rel in mapper.relationships:
                name = rel.key
                try:
                    value = getattr(self, name)
                except Exception:
                    value = None
                if value is None:
                    result[name] = None
                else:
                    if rel.uselist:
                        result[name] = [
                            item.as_dict(include_relationships=False) if hasattr(item, 'as_dict') else str(item)
                            for item in value
                        ]
                    else:
                        result[name] = value.as_dict(include_relationships=False) if hasattr(value, 'as_dict') else str(value)
        return result


# ---------------- CORE TABLES ---------------- #

class Repository(ModelMixin, db.Model):
    __tablename__ = "repository"
    id = Column(String(36), primary_key=True)
    owner = Column(Text, nullable=False)
    name = Column(Text, nullable=False)


class Branch(ModelMixin, db.Model):
    __tablename__ = "branch"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    repository_id = Column(String(36), ForeignKey("repository.id"))


class Commit(ModelMixin, db.Model):
    __tablename__ = "commit"
    id = Column(String(36), primary_key=True)
    sha = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    author = Column(Text, nullable=False)
    message = Column(Text, nullable=True)

    branch_id = Column(String(36), ForeignKey("branch.id"))


class File(ModelMixin, db.Model):
    __tablename__ = "file"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    commit_id = Column(String(36), ForeignKey("commit.id"))


class Function(ModelMixin, db.Model):
    __tablename__ = "function"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)
    line_position = Column(Integer)

    file_id = Column(String(36), ForeignKey("file.id"))


class IdentifiableEntity(ModelMixin, db.Model):
    __tablename__ = "identifiable_entity"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)


class FileIdentifiableEntity(ModelMixin, db.Model):
    __tablename__ = "file_identifiable_entity"

    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), ForeignKey("file.id"))
    identifiable_entity_id = Column(String(36), ForeignKey("identifiable_entity.id"))
    line_position = Column(Integer)


class IdentifiableEntityCount(ModelMixin, db.Model):
    __tablename__ = "identifiable_entity_count"
    id = Column(String(36), primary_key=True)
    count = Column(Integer)

    identifiable_entity_id = Column(String(36), ForeignKey("identifiable_entity.id"))
    commit_id = Column(String(36), ForeignKey("commit.id"))


class ComplexityCount(ModelMixin, db.Model):
    __tablename__ = "complexity_count"
    id = Column(String(36), primary_key=True)
    total_complexity = Column(Integer)
    function_count = Column(Integer)
    average_complexity = Column(Float)

    commit_id = Column(String(36), ForeignKey("commit.id"))


class Complexity(ModelMixin, db.Model):
    __tablename__ = "complexity"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("function.id"))


class Coverage(ModelMixin, db.Model):
    __tablename__ = "coverage"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("function.id"))


class Size(ModelMixin, db.Model):
    __tablename__ = "size"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("function.id"))


class Tests(ModelMixin, db.Model):
    __tablename__ = "test"
    id = Column(String(36), primary_key=True)
    passing_test_number = Column(Integer)
    failing_test_number = Column(Integer)

    branch_id = Column(String(36), ForeignKey("branch.id"))


class FileTestCoverage(ModelMixin, db.Model):
    __tablename__ = "file_test_coverage"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    file_id = Column(String(36), ForeignKey("file.id"))

class FileDuplication(ModelMixin, db.Model): 
    __tablename__ = "file_duplication"
    id = Column(String(36), primary_key = True)
    
    duplication_id = Column(String(36), ForeignKey("duplication.id"))
    file_id = Column(String(36), ForeignKey("file.id"))

class Duplication(ModelMixin, db.Model): 
    __tablename__ = "duplication"
    id = Column(String(36), primary_key = True)
    text = Column(Text)