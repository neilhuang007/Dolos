"""XML manipulation for injecting track changes into DOCX files."""

import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import tempfile

from lxml import etree

from .models import Sentence


class TrackChangesInjector:
    """Inject track changes XML into DOCX files."""

    # XML namespaces used in DOCX
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    }

    def __init__(self):
        """Initialize track changes injector."""
        pass

    def inject_track_changes(
        self,
        docx_path: str,
        sentences: List[Sentence],
        output_path: Optional[str] = None,
        accept_changes: bool = False
    ) -> str:
        """Inject track changes for each sentence into a DOCX file.

        Args:
            docx_path: Path to source DOCX file
            sentences: List of Sentence objects with timestamps
            output_path: Output path (if None, overwrites input)
            accept_changes: If True, accept all changes (text becomes final, not suggestions)

        Returns:
            Path to modified document
        """
        if output_path is None:
            output_path = docx_path

        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract DOCX (it's a ZIP file)
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # Modify document.xml
            doc_xml_path = temp_path / 'word' / 'document.xml'

            if accept_changes:
                # Add sentences as final text (no track changes)
                self._add_clean_text(doc_xml_path, sentences)
            else:
                # Add sentences with track changes
                self._inject_changes_into_xml(doc_xml_path, sentences)
                # Enable track changes in settings.xml
                settings_xml_path = temp_path / 'word' / 'settings.xml'
                self._enable_track_changes(settings_xml_path)

            # Repackage as DOCX
            self._zip_directory(temp_path, output_path)

        return output_path

    def _inject_changes_into_xml(self, xml_path: Path, sentences: List[Sentence]):
        """Inject track changes into document.xml.

        Args:
            xml_path: Path to document.xml
            sentences: List of Sentence objects
        """
        # Parse XML
        tree = etree.parse(str(xml_path))
        root = tree.getroot()

        # Find the body element
        body = root.find('.//w:body', namespaces=self.NAMESPACES)

        if body is None:
            raise ValueError("Could not find document body")

        # Remove existing paragraphs
        for para in body.findall('w:p', namespaces=self.NAMESPACES):
            body.remove(para)

        # Add sentences with track changes
        for idx, sentence in enumerate(sentences):
            # Create paragraph
            para = etree.SubElement(body, f"{{{self.NAMESPACES['w']}}}p")

            # Create insertion (track change)
            ins = etree.SubElement(para, f"{{{self.NAMESPACES['w']}}}ins")

            # Set track change attributes
            ins.set(f"{{{self.NAMESPACES['w']}}}id", str(sentence.revision_id))
            ins.set(f"{{{self.NAMESPACES['w']}}}author", sentence.author)

            # Format timestamp for Word (ISO 8601 format)
            timestamp_str = sentence.modified_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            ins.set(f"{{{self.NAMESPACES['w']}}}date", timestamp_str)

            # Create run (text container)
            run = etree.SubElement(ins, f"{{{self.NAMESPACES['w']}}}r")

            # Add text
            text_elem = etree.SubElement(run, f"{{{self.NAMESPACES['w']}}}t")
            text_elem.text = sentence.sentence_text

            # Add space after sentence if not the last one
            if idx < len(sentences) - 1:
                space_run = etree.SubElement(ins, f"{{{self.NAMESPACES['w']}}}r")
                space_text = etree.SubElement(space_run, f"{{{self.NAMESPACES['w']}}}t")
                space_text.set(f"{{{self.NAMESPACES['w']}}}space", "preserve")
                space_text.text = " "

        # Write modified XML
        tree.write(
            str(xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _enable_track_changes(self, settings_xml_path: Path):
        """Enable track changes in settings.xml.

        Args:
            settings_xml_path: Path to settings.xml
        """
        if not settings_xml_path.exists():
            # Create minimal settings.xml if it doesn't exist
            self._create_settings_xml(settings_xml_path)
            return

        # Parse existing settings
        tree = etree.parse(str(settings_xml_path))
        root = tree.getroot()

        # Check if trackRevisions already exists
        track_revisions = root.find('.//w:trackRevisions', namespaces=self.NAMESPACES)

        if track_revisions is None:
            # Add trackRevisions element
            track_revisions = etree.SubElement(root, f"{{{self.NAMESPACES['w']}}}trackRevisions")

        # Write modified settings
        tree.write(
            str(settings_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _create_settings_xml(self, settings_xml_path: Path):
        """Create a minimal settings.xml with track changes enabled.

        Args:
            settings_xml_path: Path to create settings.xml
        """
        root = etree.Element(
            f"{{{self.NAMESPACES['w']}}}settings",
            nsmap={'w': self.NAMESPACES['w']}
        )

        # Add trackRevisions
        etree.SubElement(root, f"{{{self.NAMESPACES['w']}}}trackRevisions")

        # Write XML
        tree = etree.ElementTree(root)
        settings_xml_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            str(settings_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _add_clean_text(self, xml_path: Path, sentences: List[Sentence]):
        """Add sentences as clean final text (no track changes).

        Args:
            xml_path: Path to document.xml
            sentences: List of Sentence objects
        """
        # Parse XML
        tree = etree.parse(str(xml_path))
        root = tree.getroot()

        # Find the body element
        body = root.find('.//w:body', namespaces=self.NAMESPACES)

        if body is None:
            raise ValueError("Could not find document body")

        # Remove existing paragraphs
        for para in body.findall('w:p', namespaces=self.NAMESPACES):
            body.remove(para)

        # Add sentences as clean text (no track changes)
        for idx, sentence in enumerate(sentences):
            # Create paragraph
            para = etree.SubElement(body, f"{{{self.NAMESPACES['w']}}}p")

            # Create run (text container) - NO insertion tag
            run = etree.SubElement(para, f"{{{self.NAMESPACES['w']}}}r")

            # Add text
            text_elem = etree.SubElement(run, f"{{{self.NAMESPACES['w']}}}t")
            text_elem.text = sentence.sentence_text

            # Add space after sentence if not the last one
            if idx < len(sentences) - 1:
                space_run = etree.SubElement(para, f"{{{self.NAMESPACES['w']}}}r")
                space_text = etree.SubElement(space_run, f"{{{self.NAMESPACES['w']}}}t")
                space_text.set(f"{{{self.NAMESPACES['w']}}}space", "preserve")
                space_text.text = " "

        # Write modified XML
        tree.write(
            str(xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _zip_directory(self, directory: Path, output_path: str):
        """Zip directory contents to create DOCX file.

        Args:
            directory: Directory to zip
            output_path: Output DOCX path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(directory)
                    zipf.write(file_path, arcname)
