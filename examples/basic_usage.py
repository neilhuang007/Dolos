"""Basic usage examples for Dolos."""

from datetime import datetime
from pathlib import Path
from dolos.text_parser import split_into_sentences
from dolos.metadata_manager import MetadataManager
from dolos.document_builder import DocumentBuilder
from dolos.xml_injector import TrackChangesInjector


def example_create_document():
    """Example: Create a document with fake edit history."""
    # Sample text
    text = """
    This is the first sentence of my document.
    This is the second sentence with different content.
    Finally, this is the third and last sentence.
    """

    # Parse into sentences
    sentences = split_into_sentences(text)
    print(f"Parsed {len(sentences)} sentences")

    # Initialize managers
    metadata_mgr = MetadataManager("data/dolos.db")
    doc_builder = DocumentBuilder()
    track_injector = TrackChangesInjector()

    # Create document with metadata
    start_time = datetime(2025, 1, 1, 10, 0, 0)
    doc = metadata_mgr.create_document(
        filename="example.docx",
        sentences=sentences,
        start_timestamp=start_time,
        min_interval_seconds=60,
        max_interval_seconds=300,
        author="John Doe"
    )

    # Build DOCX
    temp_path = "temp_example.docx"
    doc_builder.create_document(
        sentences=doc.sentences,
        output_path=temp_path,
        author="John Doe"
    )

    # Inject track changes
    track_injector.inject_track_changes(
        docx_path=temp_path,
        sentences=doc.sentences,
        output_path="example.docx"
    )

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)

    print("✓ Document created: example.docx")
    print(f"  Sentences: {len(sentences)}")
    print(f"  Time range: {doc.created_at} → {doc.last_modified}")


def example_view_metadata():
    """Example: View metadata for a document."""
    metadata_mgr = MetadataManager("data/dolos.db")

    metadata = metadata_mgr.get_document_metadata("example.docx")

    if metadata:
        print("\nDocument Metadata:")
        print(f"  Filename: {metadata['filename']}")
        print(f"  Author: {metadata['author']}")
        print(f"  Created: {metadata['created_at']}")
        print(f"  Sentences: {metadata['sentence_count']}")

        print("\nSentences:")
        for sent in metadata['sentences']:
            print(f"  [{sent['position']}] {sent['text'][:50]}...")
            print(f"      Created: {sent['created']}")


def example_edit_timestamp():
    """Example: Edit a sentence timestamp."""
    metadata_mgr = MetadataManager("data/dolos.db")
    doc_builder = DocumentBuilder()
    track_injector = TrackChangesInjector()

    # Update timestamp
    new_time = datetime(2025, 2, 15, 15, 30, 0)
    success = metadata_mgr.update_sentence_timestamp(
        document_filename="example.docx",
        sentence_position=0,
        new_timestamp=new_time
    )

    if success:
        print("✓ Timestamp updated")

        # Rebuild document
        doc = metadata_mgr.get_document_by_filename("example.docx")
        temp_path = "temp_example.docx"

        doc_builder.create_document(
            sentences=doc.sentences,
            output_path=temp_path,
            author=doc.author
        )

        track_injector.inject_track_changes(
            docx_path=temp_path,
            sentences=doc.sentences,
            output_path="example.docx"
        )

        Path(temp_path).unlink(missing_ok=True)
        print("✓ Document rebuilt with new timestamp")


if __name__ == "__main__":
    # Run examples
    print("=== Example 1: Create Document ===")
    example_create_document()

    print("\n=== Example 2: View Metadata ===")
    example_view_metadata()

    print("\n=== Example 3: Edit Timestamp ===")
    example_edit_timestamp()
