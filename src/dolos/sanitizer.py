"""Document sanitizer for removing metadata and track changes."""

import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

from lxml import etree
from docx import Document as DocxDocument


class DocumentSanitizer:
    """Sanitize Word documents by removing metadata and revision history."""

    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    def __init__(self):
        """Initialize document sanitizer."""
        pass

    def sanitize_document(
        self,
        input_path: str,
        output_path: str,
        remove_track_changes: bool = True,
        remove_metadata: bool = True,
        neutral_timestamp: Optional[datetime] = None
    ) -> str:
        """Sanitize a Word document.

        Args:
            input_path: Path to input DOCX
            output_path: Path to output sanitized DOCX
            remove_track_changes: Whether to remove track changes
            remove_metadata: Whether to remove/neutralize metadata
            neutral_timestamp: Timestamp to use for neutralization (if None, uses epoch)

        Returns:
            Path to sanitized document
        """
        if neutral_timestamp is None:
            neutral_timestamp = datetime(2000, 1, 1, 0, 0, 0)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract DOCX
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            if remove_track_changes:
                self._remove_track_changes(temp_path / 'word' / 'document.xml')
                self._disable_track_changes(temp_path / 'word' / 'settings.xml')

            if remove_metadata:
                self._sanitize_metadata(
                    temp_path / 'docProps' / 'core.xml',
                    neutral_timestamp
                )
                self._sanitize_app_properties(temp_path / 'docProps' / 'app.xml')

            # Repackage
            self._zip_directory(temp_path, output_path)

        return output_path

    def _remove_track_changes(self, doc_xml_path: Path):
        """Remove track changes from document.xml.

        Args:
            doc_xml_path: Path to document.xml
        """
        if not doc_xml_path.exists():
            return

        tree = etree.parse(str(doc_xml_path))
        root = tree.getroot()

        # Find all insertions and deletions
        for ins in root.findall('.//w:ins', namespaces=self.NAMESPACES):
            # Move content out of insertion tag
            parent = ins.getparent()
            index = parent.index(ins)

            # Move all children to parent
            for child in ins:
                parent.insert(index, child)
                index += 1

            # Remove the ins tag
            parent.remove(ins)

        # Remove deletions entirely
        for dele in root.findall('.//w:del', namespaces=self.NAMESPACES):
            parent = dele.getparent()
            parent.remove(dele)

        # Remove other revision marks
        for elem_name in ['w:moveFrom', 'w:moveTo', 'w:rPrChange', 'w:pPrChange']:
            for elem in root.findall(f'.//{elem_name}', namespaces=self.NAMESPACES):
                parent = elem.getparent()
                if parent is not None:
                    parent.remove(elem)

        # Write cleaned XML
        tree.write(
            str(doc_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _disable_track_changes(self, settings_xml_path: Path):
        """Disable track changes in settings.xml.

        Args:
            settings_xml_path: Path to settings.xml
        """
        if not settings_xml_path.exists():
            return

        tree = etree.parse(str(settings_xml_path))
        root = tree.getroot()

        # Remove trackRevisions element
        for track_rev in root.findall('.//w:trackRevisions', namespaces=self.NAMESPACES):
            parent = track_rev.getparent()
            parent.remove(track_rev)

        tree.write(
            str(settings_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _sanitize_metadata(self, core_xml_path: Path, neutral_timestamp: datetime):
        """Sanitize core metadata properties.

        Args:
            core_xml_path: Path to core.xml
            neutral_timestamp: Timestamp to use
        """
        if not core_xml_path.exists():
            return

        tree = etree.parse(str(core_xml_path))
        root = tree.getroot()

        # Format timestamp
        timestamp_str = neutral_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Clear/neutralize various properties
        properties_to_clear = [
            ('dc:creator', 'Anonymous'),
            ('dc:title', ''),
            ('dc:subject', ''),
            ('dc:description', ''),
            ('cp:lastModifiedBy', 'Anonymous'),
            ('cp:revision', '1'),
            ('cp:keywords', '')
        ]

        for prop_name, default_value in properties_to_clear:
            elem = root.find(f'.//{prop_name}', namespaces=self.NAMESPACES)
            if elem is not None:
                elem.text = default_value

        # Set neutral timestamps
        timestamp_properties = ['dcterms:created', 'dcterms:modified']
        for prop_name in timestamp_properties:
            elem = root.find(f'.//{prop_name}', namespaces=self.NAMESPACES)
            if elem is not None:
                elem.text = timestamp_str

        tree.write(
            str(core_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _sanitize_app_properties(self, app_xml_path: Path):
        """Sanitize application properties.

        Args:
            app_xml_path: Path to app.xml
        """
        if not app_xml_path.exists():
            return

        tree = etree.parse(str(app_xml_path))
        root = tree.getroot()

        # Properties to clear
        ns = {'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'}

        properties_to_clear = [
            'Company', 'Manager', 'AppVersion', 'Application'
        ]

        for prop_name in properties_to_clear:
            elem = root.find(f'.//ep:{prop_name}', namespaces=ns)
            if elem is not None:
                elem.text = ''

        tree.write(
            str(app_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

    def _zip_directory(self, directory: Path, output_path: str):
        """Zip directory to create DOCX.

        Args:
            directory: Directory to zip
            output_path: Output path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(directory)
                    zipf.write(file_path, arcname)
