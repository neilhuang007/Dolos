# Dolos Usage Examples

## Issue 1: Text Appears as "Suggestions" (Track Changes)

### Problem
When you create a document, all text shows up as track changes (suggestions/insertions) in Microsoft Word instead of final text.

### Solution
Use the `--no-track-changes` flag to create a clean document:

```bash
# Command-line mode
dolos create "Your text here." --no-track-changes --output clean.docx

# Or from file
dolos create --input-file text.txt --no-track-changes --output clean.docx
```

### Interactive Mode
When using interactive mode (`dolos`), you'll be prompted:

```
Step 6: Track Changes
Create clean document WITHOUT track changes?
(Track changes show edit history in Word but appear as 'suggestions')
[y/n]: y
```

Answer **`y`** to create a clean document without suggestions.

### When to Use Each Mode

| Mode | Use Case |
|------|----------|
| **With Track Changes** (default) | Show detailed edit history in Word; timestamps visible per sentence |
| **Without Track Changes** (`--no-track-changes`) | Clean final document; no suggestions; professional appearance |

---

## Issue 2: Edit Document Metadata (Total Edit Time, Title, etc.)

### Problem
You want to customize document properties like:
- Total editing time (编辑时间总计)
- Title (标题)
- Subject
- Keywords/Tags (标记)
- Comments (备注)

### Solution: Command-Line Mode

```bash
dolos create "Document text here." \
  --output document.docx \
  --title "My Document Title" \
  --subject "Document Subject" \
  --keywords "keyword1, keyword2, tag1" \
  --comments "Internal notes go here" \
  --total-edit-time 43 \
  --no-track-changes
```

### Solution: Interactive Mode

Run `dolos` and when you reach Step 5:

```
Step 5: Document Metadata (Optional)
Add document metadata (title, keywords, etc.)? [y/n]: y

Document title: My Document Title
Document subject: Confidential Report
Keywords/tags: government, classified, redacted
Comments: Approved for release
Total editing time (minutes): 43
```

---

## Complete Examples

### Example 1: Clean Professional Document

```bash
dolos create --input-file report.txt \
  --output final_report.docx \
  --no-track-changes \
  --title "Q4 Financial Report" \
  --subject "Finance" \
  --author "Finance Department" \
  --keywords "finance, Q4, report, 2024" \
  --comments "Approved by CFO" \
  --total-edit-time 120 \
  --start-date "2024-10-01 09:00:00"
```

**Result:**
- Clean document (no suggestions)
- Custom title, subject, keywords visible in Word properties
- Total editing time: 120 minutes
- Backdated to October 1, 2024

---

### Example 2: Document with Visible Edit History

```bash
dolos create "Sentence one. Sentence two. Sentence three." \
  --output tracked_doc.docx \
  --title "Draft Document" \
  --author "Editor Team" \
  --total-edit-time 25 \
  --min-interval 60 \
  --max-interval 300
```

**Result:**
- Each sentence shows as track change with timestamp
- Edit history visible in Word's Review pane
- Total editing time: 25 minutes
- Timestamps spread over 2-5 minutes per sentence

---

### Example 3: Government Document Redaction

```bash
dolos create --input-file classified_content.txt \
  --output public_release.docx \
  --no-track-changes \
  --title "UNCLASSIFIED" \
  --subject "Public Information Release" \
  --author "Redaction Office" \
  --comments "Sensitive information removed per security protocols" \
  --total-edit-time 90 \
  --start-date "2024-03-15 10:00:00"
```

**Result:**
- Clean document ready for public release
- No track changes or edit suggestions
- Custom metadata for official use
- Backdated creation time
- 90 minutes total editing time

---

### Example 4: Interactive Mode Complete Walkthrough

```bash
$ dolos

What would you like to do? create

Step 1: Text Content
How would you like to input text? paste

Enter your text below:
When done, type 'END' on a new line and press Enter

This is the first sentence of the document.
This is the second sentence with more content.
This is the final sentence.
END

> Parsed 3 sentences

Step 2: Output Settings
Output filename (output.docx): my_document.docx
Document author (Dolos): John Doe

Step 3: Timestamp Configuration
Use custom start date? [y/n]: y
Start date/time (2025-01-08 21:00:00): 2024-06-15 10:00:00

Step 4: Edit Interval Settings
Minimum seconds between edits (30): 60
Maximum seconds between edits (300): 600

Step 5: Document Metadata (Optional)
Add document metadata (title, keywords, etc.)? [y/n]: y
Document title: Important Document
Document subject: Business Planning
Keywords/tags: planning, strategy, 2024
Comments: Draft for review
Total editing time (minutes): 45

Step 6: Track Changes
Create clean document WITHOUT track changes?
(Track changes show edit history in Word but appear as 'suggestions')
[y/n]: y

Database path (data/dolos.db): [Press Enter]

Summary:
  Text: 156 characters, 3 sentences
  Output: my_document.docx
  Author: John Doe
  Start: 2024-06-15 10:00:00
  Intervals: 60-600 seconds
  Track changes: No (clean document)
  Title: Important Document
  Total edit time: 45 minutes

Create document? [Y/n]: y

Creating document metadata...
> Metadata stored in database
Building Word document...
Creating clean document (no track changes)...
Setting total editing time...

SUCCESS: Document created successfully!
Output: my_document.docx
Sentences: 3
Time range: 2024-06-15 10:00:00 -> 2024-06-15 10:15:32
```

---

## Viewing Metadata in Microsoft Word

After creating your document:

1. Open the `.docx` file in Microsoft Word
2. Go to **File** → **Info**
3. Click **Properties** → **Advanced Properties**
4. See all your custom metadata:
   - **Title**: [Your title]
   - **Subject**: [Your subject]
   - **Keywords**: [Your tags]
   - **Comments**: [Your comments]
   - **Total Editing Time**: [Your specified minutes]
   - **Created**: [Your start date]
   - **Modified**: [Calculated end date]

---

## Quick Reference

| Feature | Flag | Example |
|---------|------|---------|
| No track changes | `--no-track-changes` | `dolos create "text" --no-track-changes` |
| Set title | `--title` | `--title "Document Title"` |
| Set subject | `--subject` | `--subject "Report"` |
| Set keywords/tags | `--keywords` | `--keywords "tag1, tag2"` |
| Set comments | `--comments` | `--comments "Notes here"` |
| Set edit time | `--total-edit-time` | `--total-edit-time 60` |
| Set author | `--author` | `--author "John Doe"` |
| Backdate document | `--start-date` | `--start-date "2024-01-01 10:00:00"` |
| Interval range | `--min-interval --max-interval` | `--min-interval 60 --max-interval 600` |

---

## Common Use Cases

### Clean Professional Document
```bash
dolos create --input-file text.txt --no-track-changes --output final.docx
```

### Document with Full Metadata
```bash
dolos create "text" --title "Title" --subject "Subject" --keywords "tags" --total-edit-time 60 --no-track-changes -o doc.docx
```

### Backdated Document
```bash
dolos create "text" --start-date "2023-01-01 09:00:00" --no-track-changes -o old.docx
```

### Show Edit History (Track Changes)
```bash
dolos create "text" -o tracked.docx
# (default behavior - shows track changes)
```

---

## Troubleshooting

**Q: Text appears as suggestions in Word?**
A: Use `--no-track-changes` flag

**Q: How to edit document metadata?**
A: Use `--title`, `--subject`, `--keywords`, `--comments`, `--total-edit-time` flags

**Q: How to set total editing time?**
A: Use `--total-edit-time 43` (where 43 is minutes)

**Q: How to backdate a document?**
A: Use `--start-date "2024-01-01 10:00:00"`

**Q: How to make document look official/final?**
A: Use `--no-track-changes` + metadata flags

---

**For more help:**
```bash
dolos create --help
dolos --help
```

Or read the full documentation in `docs/USER_GUIDE.md`
