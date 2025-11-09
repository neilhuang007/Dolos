"""SQLAlchemy models for metadata storage."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Document(Base):
    """Represents a Word document with metadata."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_modified = Column(DateTime, nullable=False, default=datetime.utcnow)
    author = Column(String(200), default="Dolos")
    last_modified_by = Column(String(200), default="Dolos")

    # Relationship to sentences
    sentences = relationship("Sentence", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


class Sentence(Base):
    """Represents a sentence within a document with its metadata."""

    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    sentence_text = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)  # Order in document
    created_timestamp = Column(DateTime, nullable=False)
    modified_timestamp = Column(DateTime, nullable=False)
    author = Column(String(200), default="Dolos")
    revision_id = Column(Integer, default=1)  # For track changes

    # Relationship to document
    document = relationship("Document", back_populates="sentences")

    def __repr__(self):
        return f"<Sentence(id={self.id}, position={self.position}, text='{self.sentence_text[:30]}...')>"


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, db_path: str = "data/dolos.db"):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get a new database session.

        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
