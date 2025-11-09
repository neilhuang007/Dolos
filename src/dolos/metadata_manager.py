"""Metadata management for documents and sentences."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Document, Sentence, DatabaseManager


class MetadataManager:
    """Manages document and sentence metadata in the database."""

    def __init__(self, db_path: str = "data/dolos.db"):
        """Initialize metadata manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.create_tables()

    def create_document(
        self,
        filename: str,
        sentences: List[str],
        start_timestamp: Optional[datetime] = None,
        min_interval_seconds: int = 30,
        max_interval_seconds: int = 300,
        author: str = "Dolos"
    ) -> Document:
        """Create a new document with sentences in the database.

        Args:
            filename: Name of the document
            sentences: List of sentence strings
            start_timestamp: Starting timestamp for first sentence
            min_interval_seconds: Minimum seconds between sentence edits (default: 30)
            max_interval_seconds: Maximum seconds between sentence edits (default: 300)
            author: Author name

        Returns:
            Created Document object
        """
        session = self.db_manager.get_session()

        try:
            # Use current time if no start timestamp provided
            if start_timestamp is None:
                start_timestamp = datetime.utcnow()

            # Create document
            doc = Document(
                filename=filename,
                created_at=start_timestamp,
                last_modified=start_timestamp,
                author=author,
                last_modified_by=author
            )
            session.add(doc)
            session.flush()  # Get document ID

            # Create sentences with randomized intervals
            current_timestamp = start_timestamp
            for idx, sentence_text in enumerate(sentences):
                sentence = Sentence(
                    document_id=doc.id,
                    sentence_text=sentence_text,
                    position=idx,
                    created_timestamp=current_timestamp,
                    modified_timestamp=current_timestamp,
                    author=author,
                    revision_id=idx + 1
                )
                session.add(sentence)

                # Generate random interval for next sentence
                if idx < len(sentences) - 1:  # Don't increment after last sentence
                    import random
                    from datetime import timedelta
                    interval = random.randint(min_interval_seconds, max_interval_seconds)
                    current_timestamp = current_timestamp + timedelta(seconds=interval)

            # Update document last_modified to match last sentence
            doc.last_modified = current_timestamp

            session.commit()

            # Eagerly load all sentences and their attributes before closing session
            doc_id = doc.id
            doc_filename = doc.filename
            doc_created = doc.created_at
            doc_modified = doc.last_modified
            doc_author = doc.author
            doc_last_modified_by = doc.last_modified_by

            # Load all sentences into memory
            sentences_data = []
            for sent in doc.sentences:
                sentences_data.append({
                    'id': sent.id,
                    'document_id': sent.document_id,
                    'sentence_text': sent.sentence_text,
                    'position': sent.position,
                    'created_timestamp': sent.created_timestamp,
                    'modified_timestamp': sent.modified_timestamp,
                    'author': sent.author,
                    'revision_id': sent.revision_id
                })

            session.close()

            # Create new detached objects
            new_doc = Document(
                filename=doc_filename,
                created_at=doc_created,
                last_modified=doc_modified,
                author=doc_author,
                last_modified_by=doc_last_modified_by
            )
            new_doc.id = doc_id

            # Recreate sentences
            new_doc.sentences = []
            for sdata in sentences_data:
                sent_obj = Sentence(**sdata)
                new_doc.sentences.append(sent_obj)

            return new_doc

        except Exception as e:
            session.rollback()
            session.close()
            raise e

    def get_document_by_filename(self, filename: str) -> Optional[Document]:
        """Get document by filename.

        Args:
            filename: Document filename

        Returns:
            Document object or None
        """
        session = self.db_manager.get_session()
        try:
            doc = session.query(Document).filter(Document.filename == filename).first()
            if doc:
                # Eagerly load sentences
                _ = doc.sentences
            return doc
        finally:
            session.close()

    def get_document_by_id(self, doc_id: int) -> Optional[Document]:
        """Get document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document object or None
        """
        session = self.db_manager.get_session()
        try:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                _ = doc.sentences
            return doc
        finally:
            session.close()

    def update_sentence_timestamp(
        self,
        document_filename: str,
        sentence_position: int,
        new_timestamp: datetime
    ) -> bool:
        """Update timestamp for a specific sentence.

        Args:
            document_filename: Document filename
            sentence_position: Position of sentence (0-indexed)
            new_timestamp: New timestamp

        Returns:
            True if successful, False otherwise
        """
        session = self.db_manager.get_session()

        try:
            doc = session.query(Document).filter(Document.filename == document_filename).first()
            if not doc:
                return False

            sentence = (
                session.query(Sentence)
                .filter(Sentence.document_id == doc.id, Sentence.position == sentence_position)
                .first()
            )

            if not sentence:
                return False

            sentence.modified_timestamp = new_timestamp

            # Update document's last_modified if this is the latest sentence
            if sentence_position == len(doc.sentences) - 1:
                doc.last_modified = new_timestamp

            session.commit()
            return True

        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_document_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get complete metadata for a document.

        Args:
            filename: Document filename

        Returns:
            Dictionary with document and sentence metadata
        """
        doc = self.get_document_by_filename(filename)
        if not doc:
            return None

        metadata = {
            "id": doc.id,
            "filename": doc.filename,
            "created_at": doc.created_at.isoformat(),
            "last_modified": doc.last_modified.isoformat(),
            "author": doc.author,
            "last_modified_by": doc.last_modified_by,
            "sentence_count": len(doc.sentences),
            "sentences": []
        }

        for sentence in doc.sentences:
            metadata["sentences"].append({
                "position": sentence.position,
                "text": sentence.sentence_text,
                "created": sentence.created_timestamp.isoformat(),
                "modified": sentence.modified_timestamp.isoformat(),
                "author": sentence.author,
                "revision_id": sentence.revision_id
            })

        return metadata

    def delete_document(self, filename: str) -> bool:
        """Delete a document and all its sentences.

        Args:
            filename: Document filename

        Returns:
            True if successful, False otherwise
        """
        session = self.db_manager.get_session()

        try:
            doc = session.query(Document).filter(Document.filename == filename).first()
            if not doc:
                return False

            session.delete(doc)
            session.commit()
            return True

        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
