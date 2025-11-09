"""Tests for metadata manager."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from dolos.metadata_manager import MetadataManager


class TestMetadataManager:
    """Test metadata management functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_create_document(self, temp_db):
        """Test creating a document with metadata."""
        mgr = MetadataManager(temp_db)

        sentences = ["First sentence.", "Second sentence.", "Third sentence."]
        doc = mgr.create_document(
            filename="test.docx",
            sentences=sentences,
            author="TestAuthor"
        )

        assert doc is not None
        assert doc.filename == "test.docx"
        assert doc.author == "TestAuthor"
        assert len(doc.sentences) == 3

    def test_get_document_by_filename(self, temp_db):
        """Test retrieving document by filename."""
        mgr = MetadataManager(temp_db)

        sentences = ["Test sentence."]
        mgr.create_document(
            filename="retrieve_test.docx",
            sentences=sentences
        )

        doc = mgr.get_document_by_filename("retrieve_test.docx")

        assert doc is not None
        assert doc.filename == "retrieve_test.docx"

    def test_update_sentence_timestamp(self, temp_db):
        """Test updating sentence timestamp."""
        mgr = MetadataManager(temp_db)

        sentences = ["First.", "Second."]
        mgr.create_document(
            filename="update_test.docx",
            sentences=sentences
        )

        new_time = datetime(2025, 6, 15, 12, 0, 0)
        success = mgr.update_sentence_timestamp(
            "update_test.docx",
            sentence_position=0,
            new_timestamp=new_time
        )

        assert success is True

        # Verify update
        doc = mgr.get_document_by_filename("update_test.docx")
        assert doc.sentences[0].modified_timestamp == new_time

    def test_get_document_metadata(self, temp_db):
        """Test getting complete document metadata."""
        mgr = MetadataManager(temp_db)

        sentences = ["Alpha.", "Beta.", "Gamma."]
        mgr.create_document(
            filename="metadata_test.docx",
            sentences=sentences
        )

        metadata = mgr.get_document_metadata("metadata_test.docx")

        assert metadata is not None
        assert metadata['filename'] == "metadata_test.docx"
        assert metadata['sentence_count'] == 3
        assert len(metadata['sentences']) == 3

    def test_delete_document(self, temp_db):
        """Test deleting document."""
        mgr = MetadataManager(temp_db)

        sentences = ["Delete me."]
        mgr.create_document(
            filename="delete_test.docx",
            sentences=sentences
        )

        success = mgr.delete_document("delete_test.docx")
        assert success is True

        # Verify deletion
        doc = mgr.get_document_by_filename("delete_test.docx")
        assert doc is None

    def test_random_intervals(self, temp_db):
        """Test that sentences have different timestamps."""
        mgr = MetadataManager(temp_db)

        sentences = ["One.", "Two.", "Three."]
        doc = mgr.create_document(
            filename="interval_test.docx",
            sentences=sentences,
            min_interval_seconds=10,
            max_interval_seconds=100
        )

        # All timestamps should be different
        timestamps = [s.created_timestamp for s in doc.sentences]
        assert len(set(timestamps)) == len(timestamps)

        # Timestamps should be in order
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]
