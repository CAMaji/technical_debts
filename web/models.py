from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import inspect
from datetime import datetime
import enum

Base = declarative_base()

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

class Repository(ModelMixin, Base):
    __tablename__ = "repositories"
    id = Column(String(36), primary_key=True)
    owner = Column(Text, nullable=False)
    name = Column(Text, nullable=False)

    branches = relationship("Branch", back_populates="repository")


class Branch(ModelMixin, Base):
    __tablename__ = "branches"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)
    repository_id = Column(String(36), ForeignKey("repositories.id"))

    repository = relationship("Repository", back_populates="branches")
    tests = relationship("Tests", back_populates="branch")
    commits = relationship("Commit", back_populates="branch")


class Commit(ModelMixin, Base):
    __tablename__ = "commits"
    id = Column(String(36), primary_key=True)
    sha = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)

    branch_id = Column(String(36), ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="commits")

    files = relationship("File", back_populates="commit")


class File(ModelMixin, Base):
    __tablename__ = "files"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    commit_id = Column(String(36), ForeignKey("commits.id"))
    commit = relationship("Commit", back_populates="files")

    functions = relationship("Function", back_populates="file")
    file_entities = relationship("FileEntities", back_populates="file")
    file_test_coverage = relationship("FileTestCoverage", back_populates="file")


class Function(ModelMixin, Base):
    __tablename__ = "functions"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)
    line_position = Column(Integer)

    file_id = Column(String(36), ForeignKey("files.id"))
    file = relationship("File", back_populates="functions")

    complexity = relationship("Complexity", back_populates="function", uselist=False)
    coverage = relationship("Coverage", back_populates="function", uselist=False)
    size = relationship("Size", back_populates="function", uselist=False)
    function_test_coverage = relationship("FunctionTestCoverage", back_populates="function")


class IdentifiableEntity(ModelMixin, Base):
    __tablename__ = "identifiable_entities"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    file_entities = relationship("FileEntities", back_populates="entity")


class FileEntities(ModelMixin, Base):
    __tablename__ = "file_entities"
    id = Column(String(36), primary_key=True)
    line_position = Column(Integer)
    name = Column(Text, nullable=False)

    file_id = Column(String(36), ForeignKey("files.id"))
    entity_id = Column(String(36), ForeignKey("identifiable_entities.id"))

    file = relationship("File", back_populates="file_entities")
    entity = relationship("IdentifiableEntity", back_populates="file_entities")


class Complexity(ModelMixin, Base):
    __tablename__ = "complexities"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("functions.id"))
    function = relationship("Function", back_populates="complexity")


class Coverage(ModelMixin, Base):
    __tablename__ = "coverages"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("functions.id"))
    function = relationship("Function", back_populates="coverage")


class Size(ModelMixin, Base):
    __tablename__ = "sizes"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("functions.id"))
    function = relationship("Function", back_populates="size")


class Tests(ModelMixin, Base):
    __tablename__ = "tests"
    id = Column(String(36), primary_key=True)
    passing_test_number = Column(Integer)
    failing_test_number = Column(Integer)

    branch_id = Column(String(36), ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="tests")


class FileTestCoverage(ModelMixin, Base):
    __tablename__ = "file_test_coverages"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    file_id = Column(String(36), ForeignKey("files.id"))
    file = relationship("File", back_populates="file_test_coverage")


class FunctionTestCoverage(ModelMixin, Base):
    __tablename__ = "function_test_coverages"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("functions.id"))
    function = relationship("Function", back_populates="function_test_coverage")