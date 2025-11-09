# Dolos User Guide

## Overview

Dolos is a command-line tool for manipulating Microsoft Word document metadata and revision history. It allows you to create documents with fake edit histories, edit timestamps at sentence-level granularity, and sanitize documents by removing all metadata.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from source

```bash
# Clone or navigate to the Dolos directory
cd Dolos

# Install in development mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Verify installation

```bash
dolos version
```

## Core Concepts

### Sentence-Level Granularity

Dolos operates at the sentence level, not word level. Each sentence in your document can have its own:
- Creation timestamp
- Modification timestamp
- Author information
- Revision ID

### Track Changes

Dolos uses Word's native track changes feature to display edit histories. Each sentence is wrapped in an insertion (`<w:ins>`) tag with custom timestamp and author information, making the history visible directly in Microsoft Word.

### Metadata Storage

Dolos maintains a SQLite database (default: `data/dolos.db`) that stores:
- Document metadata (filename, author, timestamps)
- Sentence metadata (text, position, timestamps)

This allows for:
- Precise timestamp manipulation
- Audit trails
- Document regeneration with updated metadata

## Commands

### 1. create

Create a new Word document with custom edit history.

**Basic Usage:**

```bash
# Create from direct text input
dolos create "This is sentence one. This is sentence two." -o output.docx

# Create from file
dolos create --input-file my_text.txt -o output.docx

# With custom start date
dolos create "Sample text." --start-date "2025-01-01 10:00:00" -o doc.docx
```

**Options:**

- `text` - Text content (or use --input-file)
- `--input-file, -f` - Read text from file
- `--output, -o` - Output DOCX path (default: output.docx)
- `--author, -a` - Document author (default: Dolos)
- `--start-date, -s` - Start timestamp for first sentence
- `--min-interval` - Minimum seconds between edits (default: 30)
- `--max-interval` - Maximum seconds between edits (default: 300)
- `--db` - Database path (default: data/dolos.db)

**How it works:**

1. Parses input text into sentences
2. Generates random timestamps for each sentence within specified interval bounds
3. Stores metadata in SQLite database
4. Creates DOCX with track changes showing edit history
5. Each sentence appears as an insertion with timestamp visible in Word

**Example:**

```bash
dolos create "First sentence. Second sentence. Third sentence." \
  --output example.docx \
  --author "John Doe" \
  --start-date "2024-12-01 09:00:00" \
  --min-interval 60 \
  --max-interval 600
```

This creates a document where:
- First sentence timestamp: 2024-12-01 09:00:00
- Second sentence: 1-10 minutes later (random)
- Third sentence: 1-10 minutes after second (random)

### 2. edit-timestamp

Modify the timestamp for a specific sentence.

**Usage:**

```bash
dolos edit-timestamp document.docx \
  --sentence 0 \
  --timestamp "2025-06-15 14:30:00"
```

**Options:**

- `document` - Path to DOCX file
- `--sentence, -n` - Sentence number (0-indexed)
- `--timestamp, -t` - New timestamp
- `--db` - Database path

**Note:** This command:
1. Updates the metadata in the database
2. Rebuilds the entire document with updated track changes
3. Overwrites the original file

**Example workflow:**

```bash
# Create document
dolos create "Alpha. Beta. Gamma." -o test.docx

# View metadata to see sentence numbers
dolos view-metadata test.docx

# Edit second sentence (index 1)
dolos edit-timestamp test.docx --sentence 1 --timestamp "2025-01-20 16:45:00"
```

### 3. view-metadata

Display metadata for a document.

**Usage:**

```bash
# View in terminal
dolos view-metadata document.docx

# Export to JSON
dolos view-metadata document.docx --json metadata.json
```

**Options:**

- `document` - Path to DOCX file
- `--json` - Export metadata to JSON file
- `--db` - Database path

**Output includes:**

- Document-level metadata (filename, author, created/modified times)
- Sentence count
- Table of all sentences with:
  - Position (index)
  - Text preview
  - Created timestamp
  - Modified timestamp

**Example output:**

```
Document Metadata
Filename: example.docx
Author: Dolos
Created: 2025-01-01T10:00:00
Modified: 2025-01-01T12:30:00
Sentences: 3

Sentence Details
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃  #   ┃ Text                   ┃ Created             ┃ Modified            ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 0    │ First sentence.        │ 2025-01-01 10:00:00 │ 2025-01-01 10:00:00 │
│ 1    │ Second sentence.       │ 2025-01-01 10:15:00 │ 2025-01-01 10:15:00 │
│ 2    │ Third sentence.        │ 2025-01-01 12:30:00 │ 2025-01-01 12:30:00 │
└──────┴────────────────────────┴─────────────────────┴─────────────────────┘
```

### 4. sanitize

Remove all metadata and track changes from a document.

**Usage:**

```bash
# Sanitize to new file
dolos sanitize document.docx --output clean.docx

# Overwrite original
dolos sanitize document.docx

# With custom neutral timestamp
dolos sanitize document.docx --neutral-date "2000-01-01 00:00:00"
```

**Options:**

- `document` - Path to DOCX file to sanitize
- `--output, -o` - Output path (default: overwrites input)
- `--keep-content` - Keep document content (default: True)
- `--neutral-date` - Neutral timestamp to use (default: 2000-01-01 00:00:00)
- `--db` - Database path

**What gets removed:**

- All track changes (insertions, deletions, moves)
- Author information
- Document creation/modification timestamps (set to neutral date)
- Revision history
- Company, manager, application info
- Custom properties

**Use cases:**

- Prevent information leakage before document release
- Remove forensic evidence of editing timeline
- Clean documents for public distribution
- Reset document metadata to neutral state

### 5. version

Display version information.

```bash
dolos version
```

## Timestamp Formats

Dolos supports multiple timestamp formats:

- `YYYY-MM-DD HH:MM:SS` - Full datetime (e.g., 2025-06-15 14:30:00)
- `YYYY-MM-DDTHH:MM:SS` - ISO format (e.g., 2025-06-15T14:30:00)
- `YYYY-MM-DD HH:MM` - Date and hour/minute (e.g., 2025-06-15 14:30)
- `YYYY-MM-DD` - Date only (e.g., 2025-06-15)
- `YYYY/MM/DD HH:MM:SS` - Alternative separator
- `YYYY/MM/DD` - Date only with slashes

All timestamps are stored in UTC.

## Advanced Usage

### Creating Realistic Edit Histories

For documents that need to appear organically edited:

```bash
# Longer intervals for realistic pacing
dolos create --input-file document.txt \
  --min-interval 300 \
  --max-interval 3600 \
  --start-date "2024-10-01 09:00:00"
```

This creates edits spanning 5 minutes to 1 hour apart.

### Backdating Documents

```bash
# Create document that appears to be from 2020
dolos create "Historical document text." \
  --start-date "2020-03-15 10:00:00" \
  --output backdated.docx
```

### Batch Processing

```bash
# Process multiple files
for file in texts/*.txt; do
  output="outputs/$(basename $file .txt).docx"
  dolos create --input-file "$file" --output "$output"
done
```

### Programmatic Usage

You can also use Dolos as a Python library:

```python
from datetime import datetime
from dolos.text_parser import split_into_sentences
from dolos.metadata_manager import MetadataManager
from dolos.document_builder import DocumentBuilder
from dolos.xml_injector import TrackChangesInjector

# Parse text
text = "Your document text here. Multiple sentences."
sentences = split_into_sentences(text)

# Create metadata
mgr = MetadataManager("data/dolos.db")
doc = mgr.create_document(
    filename="output.docx",
    sentences=sentences,
    start_timestamp=datetime(2025, 1, 1, 10, 0, 0),
    min_interval_seconds=60,
    max_interval_seconds=300
)

# Build document
builder = DocumentBuilder()
builder.create_document(
    sentences=doc.sentences,
    output_path="temp.docx",
    author="Your Name"
)

# Inject track changes
injector = TrackChangesInjector()
injector.inject_track_changes(
    docx_path="temp.docx",
    sentences=doc.sentences,
    output_path="output.docx"
)
```

## Viewing Results in Microsoft Word

When you open a Dolos-generated document in Word:

1. **Track Changes Tab**: Go to Review → Track Changes
2. **Show Markup**: Ensure "All Markup" is selected
3. **Reviewing Pane**: Open to see detailed revision history
4. **Hover over text**: See author and timestamp for each insertion

The document will show each sentence as an insertion with the timestamp you specified.

## Database Management

### Default Location

The database is stored at `data/dolos.db` by default.

### Custom Database

Use `--db` flag to specify different database:

```bash
dolos create "Text" --db /path/to/custom.db -o doc.docx
```

### Backing Up

Simply copy the database file:

```bash
cp data/dolos.db data/dolos_backup.db
```

### Resetting Database

Delete the database file to start fresh:

```bash
rm data/dolos.db
```

## Troubleshooting

### "No metadata found"

The document hasn't been created with Dolos or is using a different database.

**Solution:** Check `--db` path matches the database used during creation.

### "Document not found"

File path is incorrect or file doesn't exist.

**Solution:** Verify file path and ensure file exists.

### Word shows errors opening document

XML structure may be corrupted.

**Solution:**
- Ensure all dependencies are installed correctly
- Try recreating the document
- Check that you're using a compatible Word version (2016+)

### Timestamps not showing in Word

Track changes may not be enabled.

**Solution:** In Word, go to Review → Track Changes → Display for Review → All Markup

### Permission errors

Database or output directory not writable.

**Solution:**
- Check file/directory permissions
- Ensure data/ directory exists
- Try running with appropriate permissions

## Best Practices

### For Government/Enterprise Use

1. **Sanitize before release**: Always sanitize documents before external distribution
2. **Maintain audit logs**: Keep database backups for audit trails
3. **Test in isolated environment**: Verify documents in sandboxed Word installation
4. **Document procedures**: Maintain SOPs for document handling

### For Testing

1. **Use distinct intervals**: Make test documents easily distinguishable
2. **Separate databases**: Use different databases for different test scenarios
3. **Automate workflows**: Script common testing patterns

### For Security

1. **Secure the database**: The database contains all real metadata
2. **Clean up temp files**: Ensure temporary files are deleted
3. **Verify sanitization**: Check sanitized documents with forensic tools
4. **Test compatibility**: Verify documents work on target Word versions

## Limitations

1. **Word versions**: Requires Microsoft Word 2016 or later for full compatibility
2. **Sentence parsing**: May not perfectly split all text (complex punctuation)
3. **Track changes**: Documents appear as "having changes" in Word
4. **Forensic detection**: Sophisticated forensic tools may detect manipulation
5. **File size**: Large documents with many sentences may have increased file size

## Support

For issues, bugs, or feature requests, please visit the GitHub repository or contact your system administrator.
