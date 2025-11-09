# Dolos

A command-line tool for manipulating Microsoft Word document metadata and revision history. Dolos allows you to create documents with customizable edit histories, modify timestamps at sentence-level granularity, and sanitize documents by removing metadata.

## Overview

Dolos creates Word documents (.docx) with fake editing histories by:
- Splitting text into individual sentences
- Assigning custom timestamps to each sentence
- Generating realistic revision histories with track changes
- Storing metadata in a SQLite database for future modifications

**Key Capabilities:**
- Create documents with backdated timestamps
- Edit individual sentence timestamps after creation
- Customize document metadata (title, subject, keywords, editing time)
- Three document modes: final text with timestamps, suggestions/track changes, or clean
- Sanitize documents to remove all metadata and track changes
- View and export document metadata

## Installation

**Prerequisites:**
- Python 3.9 or higher
- pip package manager

**For Users:**

```bash
cd Dolos
pip install .
```

**For Local Development:**

```bash
cd Dolos
pip install -e .
```

The `-e` flag installs in editable mode, allowing you to modify the code and see changes immediately without reinstalling.

**Verify installation:**

```bash
dolos version
```

## Quick Start

### Interactive Mode (Recommended for First-Time Users)

Launch the interactive interface:

```bash
dolos
```

Follow the step-by-step prompts to:
1. Choose an action (create/edit/sanitize/view)
2. Input text (paste directly or from file)
3. Configure timestamps and intervals
4. Set document metadata
5. Choose document mode

### Command-Line Mode

**Create a document:**

```bash
# From direct text
dolos create "First sentence. Second sentence. Third sentence." -o output.docx

# From file
dolos create --input-file document.txt -o output.docx

# With custom settings
dolos create "Text here." \
  --output doc.docx \
  --author "John Doe" \
  --start-date "2024-01-01 10:00:00" \
  --min-interval 60 \
  --max-interval 600 \
  --accept-all-changes
```

**View metadata:**

```bash
dolos view-metadata output.docx
```

**Edit timestamp:**

```bash
dolos edit-timestamp output.docx --sentence 0 --timestamp "2024-07-01 15:00:00"
```

**Sanitize document:**

```bash
dolos sanitize output.docx --output clean.docx
```

## Core Concepts

### Sentence-Level Granularity

Dolos operates at the sentence level. Each sentence can have:
- Individual creation timestamp
- Modification timestamp
- Author information
- Revision ID

### Document Modes

Three modes control how documents appear in Microsoft Word:

**1. Final Mode (Recommended)** - `--accept-all-changes`
- Text appears as final content (no suggestions)
- Timestamps preserved in metadata
- Professional appearance
- Most common use case

**2. Suggestions Mode** (default, no flag)
- Text shows as track changes with red underlines
- Author popups visible on hover
- Useful for showing detailed edit history

**3. Clean Mode** - `--no-track-changes`
- Normal text appearance
- No timestamps stored
- Minimal metadata

### Metadata Storage

Dolos maintains a SQLite database (default: `data/dolos.db`) storing:
- Document metadata (filename, author, timestamps)
- Sentence metadata (text, position, timestamps)
- Enables precise timestamp manipulation and audit trails

## Usage Examples

### Professional Document with Full Metadata

```bash
dolos create --input-file report.txt \
  --output final_report.docx \
  --accept-all-changes \
  --title "Q4 Financial Report" \
  --subject "Finance" \
  --author "Finance Department" \
  --keywords "finance, Q4, report, 2024" \
  --comments "Approved by CFO" \
  --total-edit-time 120 \
  --start-date "2024-10-01 09:00:00"
```

Result:
- Clean document without suggestions
- Custom metadata visible in Word properties
- 120 minutes total editing time
- Backdated to October 1, 2024

### Document with Visible Edit History

```bash
dolos create "Sentence one. Sentence two. Sentence three." \
  --output tracked_doc.docx \
  --title "Draft Document" \
  --author "Editor Team" \
  --min-interval 60 \
  --max-interval 300
```

Result:
- Each sentence shows as track change with timestamp
- Edit history visible in Word's Review pane
- Timestamps spread over 1-5 minutes per sentence

### Backdated Document

```bash
dolos create "Historical content here." \
  --start-date "2020-03-15 10:00:00" \
  --accept-all-changes \
  --output backdated.docx
```

### Sanitize Before Release

```bash
dolos sanitize classified_draft.docx \
  --output public_release.docx \
  --neutral-date "2000-01-01 00:00:00"
```

Removes:
- All track changes
- Author information
- Revision history
- Application metadata

## Command Reference

### create

Create a new Word document with custom edit history.

**Options:**
- `text` - Text content (or use --input-file)
- `--input-file, -f` - Read text from file
- `--output, -o` - Output DOCX path (default: output.docx)
- `--author, -a` - Document author (default: Dolos)
- `--start-date, -s` - Start timestamp for first sentence
- `--min-interval` - Minimum seconds between edits (default: 30)
- `--max-interval` - Maximum seconds between edits (default: 300)
- `--title` - Document title
- `--subject` - Document subject
- `--keywords` - Keywords/tags
- `--comments` - Document comments
- `--total-edit-time` - Total editing time in minutes
- `--accept-all-changes` - Create final document (no suggestions)
- `--no-track-changes` - Create clean document (no timestamps)
- `--db` - Database path (default: data/dolos.db)

### edit-timestamp

Modify the timestamp for a specific sentence.

```bash
dolos edit-timestamp document.docx --sentence 0 --timestamp "2025-06-15 14:30:00"
```

**Options:**
- `document` - Path to DOCX file
- `--sentence, -n` - Sentence number (0-indexed)
- `--timestamp, -t` - New timestamp
- `--db` - Database path

### view-metadata

Display metadata for a document.

```bash
dolos view-metadata document.docx
dolos view-metadata document.docx --json metadata.json
```

**Options:**
- `document` - Path to DOCX file
- `--json` - Export metadata to JSON file
- `--db` - Database path

### sanitize

Remove all metadata and track changes from a document.

```bash
dolos sanitize document.docx --output clean.docx
```

**Options:**
- `document` - Path to DOCX file
- `--output, -o` - Output path (default: overwrites input)
- `--neutral-date` - Neutral timestamp (default: 2000-01-01 00:00:00)
- `--db` - Database path

## Interactive Mode

Multi-line text input when pasting:

**Windows:**
1. Paste text (Ctrl+V)
2. Press Ctrl+Z then Enter to finish

**Linux/Mac:**
1. Paste text (Ctrl+Shift+V or Cmd+V)
2. Press Ctrl+D to finish

**Alternative:** Type `END` on a new line and press Enter

## Viewing Results in Microsoft Word

1. Open the .docx file in Microsoft Word
2. Go to **Review** tab → **Track Changes**
3. Click **Display for Review** → **All Markup**
4. Open **Reviewing Pane** to see detailed revision history
5. Hover over text to see timestamps for each sentence

For metadata:
1. Go to **File** → **Info**
2. Click **Properties** → **Advanced Properties**
3. View title, subject, keywords, comments, and total editing time

## Troubleshooting

**Text appears as suggestions in Word?**

Use `--accept-all-changes` flag to create final documents without suggestions.

**How to set total editing time?**

Use `--total-edit-time 43` where 43 is minutes.

**How to backdate a document?**

Use `--start-date "2024-01-01 10:00:00"`

**Timestamps not showing in Word?**

Enable track changes: Review → Track Changes → Display for Review → All Markup

**"No metadata found" error?**

Check that `--db` path matches the database used during document creation.

## Documentation

- `README.md` - This file (overview and quick reference)
- `docs/USER_GUIDE.md` - Comprehensive user guide with detailed examples
- `docs/TECHNICAL.md` - Technical architecture and development documentation

## Quick Reference

| Feature | Flag | Example |
|---------|------|---------|
| Final document (no suggestions) | `--accept-all-changes` | `dolos create "text" --accept-all-changes` |
| Clean document (no timestamps) | `--no-track-changes` | `dolos create "text" --no-track-changes` |
| Set title | `--title` | `--title "Document Title"` |
| Set subject | `--subject` | `--subject "Report"` |
| Set keywords | `--keywords` | `--keywords "tag1, tag2"` |
| Set comments | `--comments` | `--comments "Notes here"` |
| Set editing time | `--total-edit-time` | `--total-edit-time 60` |
| Set author | `--author` | `--author "John Doe"` |
| Backdate document | `--start-date` | `--start-date "2024-01-01 10:00:00"` |
| Edit intervals | `--min-interval --max-interval` | `--min-interval 60 --max-interval 600` |

## Common Commands

```bash
# Final professional document
dolos create --input-file text.txt --accept-all-changes --output final.docx

# Document with full metadata
dolos create "text" --title "Title" --subject "Subject" --keywords "tags" \
  --total-edit-time 60 --accept-all-changes -o doc.docx

# Backdated document
dolos create "text" --start-date "2023-01-01 09:00:00" --accept-all-changes -o old.docx

# Show edit history (track changes)
dolos create "text" -o tracked.docx

# View help
dolos --help
dolos create --help
```

## Limitations

- Requires Microsoft Word 2016 or later for full compatibility
- Sentence parsing may not perfectly handle complex punctuation
- Documents appear as "having changes" when track changes are enabled
- Sophisticated forensic tools may detect timestamp manipulation
- Large documents with many sentences may have increased file size

## License

MIT License
