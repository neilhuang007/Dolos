"""XML manipulation for injecting track changes into DOCX files."""

import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import tempfile
import random

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
        # Generate a random rsidRoot for this document session
        self.rsid_root = self._generate_rsid()

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

    def _generate_rsid(self) -> str:
        """Generate a random RSID (Revision Save ID).

        RSIDs are 8-character hexadecimal values used by Word to track editing sessions.

        Returns:
            8-character hex string
        """
        return '{:08X}'.format(random.randint(0, 0xFFFFFFFF))

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

        # Save sectPr (section properties) if it exists - it must be at the end
        sect_pr = body.find('w:sectPr', namespaces=self.NAMESPACES)
        if sect_pr is not None:
            body.remove(sect_pr)

        # Remove existing paragraphs
        for para in body.findall('w:p', namespaces=self.NAMESPACES):
            body.remove(para)

        # Add sentences with track changes
        for idx, sentence in enumerate(sentences):
            # Generate unique RSID for this edit
            rsid = self._generate_rsid()

            # Create paragraph
            para = etree.SubElement(body, f"{{{self.NAMESPACES['w']}}}p")
            # Add rsid attributes to paragraph
            para.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)
            para.set(f"{{{self.NAMESPACES['w']}}}rsidRDefault", rsid)

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
            # Add rsidR to run as well
            run.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)

            # Add text
            text_elem = etree.SubElement(run, f"{{{self.NAMESPACES['w']}}}t")
            # Add xml:space="preserve" to preserve whitespace
            text_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            text_elem.text = sentence.sentence_text

            # Add space after sentence if not the last one
            if idx < len(sentences) - 1:
                space_run = etree.SubElement(ins, f"{{{self.NAMESPACES['w']}}}r")
                space_run.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)
                space_text = etree.SubElement(space_run, f"{{{self.NAMESPACES['w']}}}t")
                space_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                space_text.text = " "

        # Re-add sectPr at the end if it existed
        if sect_pr is not None:
            body.append(sect_pr)

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

        # Add rsidRoot for better compatibility
        rsid_root_elem = root.find('.//w:rsidRoot', namespaces=self.NAMESPACES)
        if rsid_root_elem is None:
            rsid_root_elem = etree.SubElement(root, f"{{{self.NAMESPACES['w']}}}rsidRoot")
            rsid_root_elem.set(f"{{{self.NAMESPACES['w']}}}val", self.rsid_root)

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

        # Add rsidRoot
        rsid_root_elem = etree.SubElement(root, f"{{{self.NAMESPACES['w']}}}rsidRoot")
        rsid_root_elem.set(f"{{{self.NAMESPACES['w']}}}val", self.rsid_root)

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

        # Save sectPr (section properties) if it exists - it must be at the end
        sect_pr = body.find('w:sectPr', namespaces=self.NAMESPACES)
        if sect_pr is not None:
            body.remove(sect_pr)

        # Remove existing paragraphs
        for para in body.findall('w:p', namespaces=self.NAMESPACES):
            body.remove(para)

        # Add sentences as clean text (no track changes)
        for idx, sentence in enumerate(sentences):
            # Generate unique RSID for this paragraph
            rsid = self._generate_rsid()

            # Create paragraph
            para = etree.SubElement(body, f"{{{self.NAMESPACES['w']}}}p")
            # Add rsid attributes even for clean text
            para.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)
            para.set(f"{{{self.NAMESPACES['w']}}}rsidRDefault", rsid)

            # Create run (text container) - NO insertion tag
            run = etree.SubElement(para, f"{{{self.NAMESPACES['w']}}}r")
            run.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)

            # Add text
            text_elem = etree.SubElement(run, f"{{{self.NAMESPACES['w']}}}t")
            # Add xml:space="preserve" to preserve whitespace
            text_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            text_elem.text = sentence.sentence_text

            # Add space after sentence if not the last one
            if idx < len(sentences) - 1:
                space_run = etree.SubElement(para, f"{{{self.NAMESPACES['w']}}}r")
                space_run.set(f"{{{self.NAMESPACES['w']}}}rsidR", rsid)
                space_text = etree.SubElement(space_run, f"{{{self.NAMESPACES['w']}}}t")
                space_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                space_text.text = " "

        # Re-add sectPr at the end if it existed
        if sect_pr is not None:
            body.append(sect_pr)

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
            # Add [Content_Types].xml first WITHOUT compression for Word compatibility
            content_types = directory / '[Content_Types].xml'
            if content_types.exists():
                zipf.write(content_types, '[Content_Types].xml', compress_type=zipfile.ZIP_STORED)

            # Add _rels/.rels second
            rels_file = directory / '_rels' / '.rels'
            if rels_file.exists():
                zipf.write(rels_file, '_rels/.rels')

            # Add all other files
            for file_path in sorted(directory.rglob('*')):
                if file_path.is_file():
                    arcname = file_path.relative_to(directory)
                    # Skip files we already added
                    if str(arcname) not in ('[Content_Types].xml', '_rels/.rels'):
                        zipf.write(file_path, arcname)
