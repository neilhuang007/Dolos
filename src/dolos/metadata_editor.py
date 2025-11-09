"""Direct XML editing for advanced document properties."""

import zipfile
import tempfile
from pathlib import Path
from lxml import etree
from typing import Optional


class MetadataEditor:
    """Edit document metadata that python-docx doesn't expose."""

    NAMESPACES = {
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    @staticmethod
    def set_total_edit_time(docx_path: str, minutes: int) -> None:
        """Set the total editing time in the document.

        Args:
            docx_path: Path to DOCX file
            minutes: Total editing time in minutes
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract DOCX
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # Edit core.xml
            core_xml_path = temp_path / 'docProps' / 'core.xml'
            if not core_xml_path.exists():
                return

            tree = etree.parse(str(core_xml_path))
            root = tree.getroot()

            # Remove existing TotalTime element if present
            for elem in root.findall('.//cp:TotalTime', namespaces=MetadataEditor.NAMESPACES):
                root.remove(elem)

            # Add TotalTime element
            # Format: PT#M where # is minutes
            total_time_elem = etree.Element(f"{{{MetadataEditor.NAMESPACES['cp']}}}TotalTime")
            total_time_elem.text = f"PT{minutes}M"
            root.append(total_time_elem)

            # Write modified XML
            tree.write(
                str(core_xml_path),
                xml_declaration=True,
                encoding='UTF-8',
                standalone=True,
                pretty_print=False
            )

            # Repackage DOCX
            MetadataEditor._zip_directory(temp_path, docx_path)

    @staticmethod
    def _zip_directory(directory: Path, output_path: str):
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
