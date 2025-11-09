# Technical Documentation

## Architecture Overview

Dolos is built using a modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   CLI (Typer)   │  ← User interface
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───────┐
│Parser│  │Sanitizer │
└───┬──┘  └──────────┘
    │
┌───▼─────────────┐
│Metadata Manager │  ← Business logic
└────┬────────────┘
     │
┌────▼─────┐  ┌──────────────┐
│ Database │  │Document       │
│ (SQLite) │  │Builder +      │
└──────────┘  │XML Injector   │
              └───────────────┘
```

## Core Components

### 1. Text Parser (`text_parser.py`)

**Purpose:** Segment input text into sentences.

**Implementation:**
- Uses regex-based sentence boundary detection
- Accounts for common abbreviations
- Handles multiple punctuation types (., !, ?)

**Key Methods:**
- `parse()` - Main parsing with regex
- `parse_simple()` - Fallback simple parsing

**Limitations:**
- May struggle with complex punctuation
- Abbreviations can cause false splits
- No ML-based parsing (intentionally simple)

### 2. Database Models (`models.py`)

**Purpose:** Data persistence layer using SQLAlchemy ORM.

**Schema:**

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    last_modified DATETIME NOT NULL,
    author TEXT,
    last_modified_by TEXT
);

CREATE TABLE sentences (
    id INTEGER PRIMARY KEY,
    document_id INTEGER FOREIGN KEY REFERENCES documents(id),
    sentence_text TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_timestamp DATETIME NOT NULL,
    modified_timestamp DATETIME NOT NULL,
    author TEXT,
    revision_id INTEGER
);
```

**Relationships:**
- One Document → Many Sentences (one-to-many)
- Cascade delete: Deleting document deletes all sentences

### 3. Metadata Manager (`metadata_manager.py`)

**Purpose:** CRUD operations for document and sentence metadata.

**Key Features:**
- Random interval generation for realistic timestamps
- Configurable min/max interval bounds
- Atomic database operations with rollback support

**Critical Methods:**

```python
create_document(
    filename: str,
    sentences: List[str],
    start_timestamp: Optional[datetime],
    min_interval_seconds: int,
    max_interval_seconds: int,
    author: str
) -> Document
```

**Timestamp Generation:**
1. Start with `start_timestamp` (or current time)
2. For each sentence:
   - Create sentence with current timestamp
   - Generate random interval: `random.randint(min, max)`
   - Increment timestamp for next sentence

### 4. Document Builder (`document_builder.py`)

**Purpose:** Create DOCX files using python-docx library.

**Process:**
1. Create new `Document()` object
2. Set core properties (author, timestamps)
3. Add sentences as paragraphs
4. Save to file

**Note:** This creates a "vanilla" DOCX. Track changes are added separately by XML Injector.

### 5. XML Injector (`xml_injector.py`)

**Purpose:** Inject track changes directly into DOCX XML structure.

**How DOCX Works:**
- DOCX is a ZIP file containing XML documents
- Main content: `word/document.xml`
- Settings: `word/settings.xml`

**Track Changes Structure:**

```xml
<w:p>  <!-- paragraph -->
  <w:ins w:id="1" w:author="Dolos" w:date="2025-01-01T10:00:00Z">
    <w:r>  <!-- run -->
      <w:t>Sentence text here.</w:t>
    </w:r>
  </w:ins>
</w:p>
```

**Process:**
1. Extract DOCX to temp directory (unzip)
2. Parse `word/document.xml` with lxml
3. Remove existing paragraphs
4. Create new paragraphs with `<w:ins>` tags
5. Set attributes: `w:id`, `w:author`, `w:date`
6. Enable track changes in `word/settings.xml`
7. Repackage as ZIP (DOCX)

**XML Namespaces:**
- `w`: `http://schemas.openxmlformats.org/wordprocessingml/2006/main`

### 6. Sanitizer (`sanitizer.py`)

**Purpose:** Remove metadata and track changes from DOCX.

**Removal Process:**

**Track Changes:**
- Find all `<w:ins>`, `<w:del>`, `<w:moveFrom>`, `<w:moveTo>` elements
- For insertions: unwrap content (keep text, remove tag)
- For deletions: remove entirely
- Remove `<w:trackRevisions>` from settings.xml

**Metadata (core.xml):**
- Set author to "Anonymous"
- Clear title, subject, description
- Set timestamps to neutral date
- Reset revision counter to 1

**Metadata (app.xml):**
- Clear Company, Manager, AppVersion fields

**Process:**
1. Extract DOCX
2. Parse and modify XMLs
3. Write back modified XMLs
4. Repackage as DOCX

### 7. CLI (`cli.py`)

**Purpose:** User-facing command-line interface.

**Framework:** Typer (modern CLI framework built on Click)

**Features:**
- Type-safe argument parsing
- Rich terminal output (colors, tables)
- Automatic help generation
- Multiple input methods (text arg, file, interactive)

**Commands:**
- `create` - Generate document
- `edit-timestamp` - Modify sentence timestamp
- `view-metadata` - Display metadata
- `sanitize` - Clean document
- `version` - Show version

## Data Flow

### Creating a Document

```
User Input (CLI)
    ↓
Text Parser → List[str] (sentences)
    ↓
Metadata Manager → Store in SQLite
    ↓
Document Builder → Create DOCX
    ↓
XML Injector → Add track changes
    ↓
Output DOCX file
```

### Editing Timestamp

```
User: document + sentence# + new timestamp
    ↓
Metadata Manager → Update SQLite
    ↓
Retrieve all sentences from DB
    ↓
Document Builder → Rebuild DOCX
    ↓
XML Injector → Re-inject track changes
    ↓
Overwrite original DOCX
```

### Sanitizing

```
Input DOCX
    ↓
Extract ZIP → Temp directory
    ↓
Parse XMLs with lxml
    ↓
Remove track changes tags
    ↓
Neutralize metadata
    ↓
Repackage ZIP → Output DOCX
```

## Technology Stack

### Core Dependencies

- **python-docx** (1.1.0+): DOCX manipulation
- **lxml** (5.0.0+): XML parsing and manipulation
- **SQLAlchemy** (2.0.0+): ORM for database
- **Typer** (0.12.0+): CLI framework
- **Rich**: Terminal formatting
- **python-dateutil**: Timestamp parsing

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking

## Security Considerations

### Timestamp Manipulation Detection

**Risk:** Forensic tools can detect timestamp manipulation by:
1. Inconsistencies between file system and internal metadata
2. Unrealistic editing patterns (e.g., edits too fast)
3. Metadata that doesn't match Word version signatures

**Mitigation:**
1. Use realistic interval ranges (min: 30s, max: 300s)
2. Ensure consistent timestamps across all fields
3. Test with forensic tools before deployment

### Database Security

**Risk:** SQLite database contains all real metadata.

**Mitigation:**
1. Store database in secure location
2. Encrypt database if handling sensitive data
3. Implement access controls
4. Regular backups with encryption

### Sanitization Thoroughness

**Risk:** Incomplete sanitization may leave traces.

**What Dolos removes:**
- Track changes XML
- Core properties (author, timestamps)
- Application properties
- Revision history

**What Dolos does NOT remove:**
- Embedded objects metadata
- Hidden text/comments (if not in track changes)
- External link references
- Printer/filesystem paths in some cases

**Recommendation:** Use multiple tools for critical sanitization.

## Performance Characteristics

### Time Complexity

- **Sentence parsing:** O(n) where n = text length
- **Database operations:** O(m) where m = sentence count
- **XML manipulation:** O(m) for injection, O(k) for sanitization where k = existing XML nodes
- **DOCX creation:** O(m)

### Space Complexity

- **Database:** ~100 bytes per sentence (metadata only)
- **DOCX file:** Standard DOCX overhead + text content + track changes XML (~2-5x text size)
- **Temp files:** Full DOCX extracted during XML operations

### Bottlenecks

1. **XML parsing/serialization** - Most expensive operation
2. **ZIP compression** - When repackaging DOCX
3. **Database I/O** - Usually negligible unless thousands of documents

### Optimization Opportunities

1. **Batch operations:** Process multiple documents in parallel
2. **XML streaming:** For very large documents
3. **Connection pooling:** For database operations
4. **Caching:** Parse XML once, modify multiple times

## Testing Strategy

### Unit Tests

- `test_text_parser.py`: Sentence segmentation
- `test_metadata_manager.py`: Database operations
- `test_utils.py`: Utility functions

### Integration Tests

Testing full workflows:
1. Create document → verify DOCX valid
2. Edit timestamp → verify changes applied
3. Sanitize → verify metadata removed

### Test Data

- Simple sentences
- Complex punctuation
- Edge cases (empty, single word, etc.)
- Various timestamp formats

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=dolos --cov-report=html

# Specific module
pytest tests/test_text_parser.py
```

## Extension Points

### Adding New Commands

```python
# In cli.py
@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Description")
):
    """Command description."""
    # Implementation
```

### Custom Sentence Parsers

```python
# Implement custom parser
class MLSentenceParser:
    def parse(self, text: str) -> List[str]:
        # ML-based parsing
        pass

# Use in create command
parser = MLSentenceParser()
sentences = parser.parse(text)
```

### Alternative Storage Backends

```python
# Implement interface
class MongoMetadataManager:
    def create_document(self, ...):
        # Store in MongoDB
        pass
```

### Custom Output Formats

```python
# Add to document_builder.py
def create_pdf_with_metadata(sentences, output_path):
    # Generate PDF with metadata
    pass
```

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Database

```bash
sqlite3 data/dolos.db
.tables
SELECT * FROM documents;
SELECT * FROM sentences;
```

### Examine DOCX Structure

```bash
# Extract DOCX
unzip document.docx -d extracted/

# View document.xml
cat extracted/word/document.xml | xmllint --format -
```

### Common Issues

**Issue:** Sentences not parsing correctly
- **Debug:** Print `split_into_sentences()` output
- **Fix:** Adjust regex or use `parse_simple()`

**Issue:** Track changes not visible in Word
- **Debug:** Check `word/settings.xml` for `<w:trackRevisions/>`
- **Fix:** Ensure XML Injector is called

**Issue:** Database locked
- **Debug:** Check for unclosed sessions
- **Fix:** Use context managers, ensure `session.close()`

## Future Enhancements

### Planned Features

1. **Interactive mode:** Launch editor for multi-line input
2. **Import metadata:** Read existing DOCX metadata into database
3. **Bulk timestamp editing:** Modify multiple sentences at once
4. **Template support:** Pre-defined metadata templates
5. **Format support:** ODT, RTF support

### Technical Improvements

1. **Async operations:** For large batch processing
2. **ML sentence parsing:** More accurate segmentation
3. **Compression:** Optimize DOCX file size
4. **Validation:** XML schema validation
5. **Caching:** Improve performance for repeated operations

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## License

MIT License - See `LICENSE` file.
