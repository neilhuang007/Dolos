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
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
        'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
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

            # Edit app.xml (Extended Properties)
            app_xml_path = temp_path / 'docProps' / 'app.xml'
            if not app_xml_path.exists():
                # Create app.xml if it doesn't exist
                MetadataEditor._create_app_xml(app_xml_path, minutes)
            else:
                # Update existing app.xml
                tree = etree.parse(str(app_xml_path))
                root = tree.getroot()

                # Remove existing TotalTime element if present
                for elem in root.findall('.//ep:TotalTime', namespaces=MetadataEditor.NAMESPACES):
                    root.remove(elem)

                # Add TotalTime element as simple integer value (in minutes)
                total_time_elem = etree.Element(f"{{{MetadataEditor.NAMESPACES['ep']}}}TotalTime")
                total_time_elem.text = str(minutes)
                root.append(total_time_elem)

                # Write modified XML
                tree.write(
                    str(app_xml_path),
                    xml_declaration=True,
                    encoding='UTF-8',
                    standalone=True,
                    pretty_print=False
                )

            # Repackage DOCX
            MetadataEditor._zip_directory(temp_path, docx_path)

    @staticmethod
    def _create_app_xml(app_xml_path: Path, minutes: int) -> None:
        """Create a minimal app.xml with TotalTime.

        Args:
            app_xml_path: Path to create app.xml
            minutes: Total editing time in minutes
        """
        # Create root element with proper namespaces
        root = etree.Element(
            f"{{{MetadataEditor.NAMESPACES['ep']}}}Properties",
            nsmap={
                None: MetadataEditor.NAMESPACES['ep'],
                'vt': MetadataEditor.NAMESPACES['vt']
            }
        )

        # Add Application element
        app_elem = etree.SubElement(root, f"{{{MetadataEditor.NAMESPACES['ep']}}}Application")
        app_elem.text = "Microsoft Office Word"

        # Add TotalTime element
        total_time_elem = etree.SubElement(root, f"{{{MetadataEditor.NAMESPACES['ep']}}}TotalTime")
        total_time_elem.text = str(minutes)

        # Write XML
        tree = etree.ElementTree(root)
        app_xml_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            str(app_xml_path),
            xml_declaration=True,
            encoding='UTF-8',
            standalone=True,
            pretty_print=False
        )

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
            # Add [Content_Types].xml first for better Word compatibility
            content_types = directory / '[Content_Types].xml'
            if content_types.exists():
                zipf.write(content_types, '[Content_Types].xml')

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
