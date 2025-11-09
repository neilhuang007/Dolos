# SOLUTION: Text Shows as "Suggestions" in Word

## The Problem
When you create a document, the text appears with **track changes** (suggestions) like this:
- Red underlines or colored text
- Author popup bubbles (showing "neil", timestamps, etc.)
- Text marked as insertions instead of final content

## The Solution: Use `--accept-all-changes`

### Command-Line Mode

```bash
dolos create "Your text here." --accept-all-changes --output document.docx
```

**With full metadata:**
```bash
dolos create --input-file text.txt \
  --accept-all-changes \
  --title "Document Title" \
  --total-edit-time 43 \
  --output final.docx
```

### Interactive Mode

When you run `dolos`, you'll see:

```
Step 6: Document Mode
Choose how the document should appear in Word:

Document mode [final/suggestions/clean] (final): final

Selected: final
  -> Text appears final with timestamps (RECOMMENDED)
```

**Choose:** `final` (this is the default and recommended)

---

## Three Document Modes

| Mode | Flag | What You See in Word | Use Case |
|------|------|---------------------|----------|
| **final** (RECOMMENDED) | `--accept-all-changes` | ✅ Normal text, no suggestions<br>✅ Timestamps preserved<br>✅ Clean professional look | **Most common use case**<br>Final documents for release |
| **suggestions** | (default, no flag) | ❌ Text shows as track changes<br>❌ Red underlines, popups<br>❌ Looks like draft | Showing detailed edit history<br>Review mode |
| **clean** | `--no-track-changes` | ✅ Normal text<br>❌ No timestamps at all<br>✅ Minimal metadata | Completely clean document |

---

## Examples

### Example 1: Final Professional Document (RECOMMENDED)
```bash
dolos create "Document content here. Second sentence." \
  --accept-all-changes \
  --title "Q4 Report" \
  --total-edit-time 43 \
  --output report.docx
```

**Result:**
- ✅ Text appears as final content (no suggestions)
- ✅ Title and editing time visible in properties
- ✅ Timestamps preserved in metadata
- ✅ Professional appearance

### Example 2: With Suggestions (Old Behavior)
```bash
dolos create "Document content here." --output draft.docx
```

**Result:**
- ❌ Text appears as track changes
- ❌ Red underlines and author popups
- ❌ Looks like draft/review mode

### Example 3: Completely Clean
```bash
dolos create "Document content here." --no-track-changes --output clean.docx
```

**Result:**
- ✅ Text appears final
- ❌ No timestamps stored
- ❌ No edit history metadata

---

## Interactive Mode Complete Example

```bash
$ dolos

Step 1: Text Content
How would you like to input text? paste

Enter your text below:
When done, type 'END' on a new line and press Enter

This is the first sentence.
This is the second sentence.
This is the final sentence.
END

> Parsed 3 sentences

Step 2: Output Settings
Output filename (output.docx): my_document.docx
Document author (Dolos): John Doe

Step 3: Timestamp Configuration
Use custom start date? [y/n]: n

Step 4: Edit Interval Settings
Minimum seconds between edits (30): 60
Maximum seconds between edits (300): 600

Step 5: Document Metadata (Optional)
Add document metadata (title, keywords, etc.)? [y/n]: y
Document title: Important Report
Document subject: Business
Keywords/tags: report, business, 2024
Comments: Final version
Total editing time (minutes): 43

Step 6: Document Mode
Choose how the document should appear in Word:

Document mode [final/suggestions/clean] (final): final

Selected: final
  -> Text appears final with timestamps (RECOMMENDED)

Database path (data/dolos.db): [Press Enter]

Summary:
  Text: 92 characters, 3 sentences
  Output: my_document.docx
  Author: John Doe
  Start: Current time
  Intervals: 60-600 seconds
  Mode: Final text with timestamps
  Title: Important Report
  Total edit time: 43 minutes

Create document? [Y/n]: y

Creating document metadata...
> Metadata stored in database
Building Word document...
Creating document with timestamps (final text)...
Setting total editing time...

SUCCESS: Document created successfully!
```

**Result in Word:**
- ✅ Text appears normal (no red underlines)
- ✅ No author popups
- ✅ Professional final document
- ✅ Metadata visible in File → Info → Properties
- ✅ Total editing time: 43 minutes

---

## Quick Fix Guide

### Problem: Text shows as suggestions with red underlines
**Solution:** Add `--accept-all-changes` flag

### Problem: Author popups appear when hovering
**Solution:** Add `--accept-all-changes` flag

### Problem: Document looks like a draft
**Solution:** Add `--accept-all-changes` flag

### Problem: Want timestamps but clean appearance
**Solution:** Add `--accept-all-changes` flag ✅

### Problem: Don't want any timestamps at all
**Solution:** Add `--no-track-changes` flag

---

## Comparison Table

| Feature | `--accept-all-changes` | Default | `--no-track-changes` |
|---------|----------------------|---------|---------------------|
| Text appearance | ✅ Final | ❌ Suggestions | ✅ Final |
| Timestamps stored | ✅ Yes | ✅ Yes | ❌ No |
| Metadata (title, etc.) | ✅ Yes | ✅ Yes | ✅ Yes |
| Total edit time | ✅ Yes | ✅ Yes | ✅ Yes |
| Professional look | ✅ Yes | ❌ No | ✅ Yes |
| Shows edit history | 🔍 In metadata | ❌ As suggestions | ❌ No |

---

## Recommended Usage

**For most use cases:**
```bash
dolos create --input-file text.txt --accept-all-changes --output final.docx
```

**Or in interactive mode, choose:** `final` (the default)

This gives you:
- ✅ Clean final text
- ✅ Timestamps preserved
- ✅ Professional appearance
- ✅ Full metadata control

---

## More Help

```bash
dolos create --help
```

See also:
- `NEW_FEATURES.txt` - Overview of new features
- `USAGE_EXAMPLES.md` - Detailed examples
- `docs/USER_GUIDE.md` - Complete user guide
