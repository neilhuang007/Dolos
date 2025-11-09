# Interactive Mode Guide

## Overview

Dolos interactive mode provides a guided, step-by-step interface for all operations. This is the recommended way to use Dolos, especially for users who prefer not to memorize command-line arguments.

## Launching Interactive Mode

Simply run `dolos` without any arguments:

```bash
dolos
```

You'll see a welcome screen:

```
╭──────────────────────────────────────────────────╮
│ Dolos - Document Metadata Manipulation Tool     │
│ Version 0.1.0                                    │
│                                                  │
│ Interactive mode - Choose your action below     │
╰──────────────────────────────────────────────────╯

What would you like to do? [create/edit/sanitize/view/quit] (create):
```

## Actions

### 1. Create Document

Creates a new Word document with fake edit history.

**Workflow:**

#### Step 1: Text Content
```
Step 1: Text Content
How would you like to input text? [paste/file] (paste):
```

**Option A - Paste Text:**
```
> paste

Enter your text (press Ctrl+D or Ctrl+Z then Enter when done):
You can paste multiple lines or type freely

[Paste or type your text here]
[Press Ctrl+D on Linux/Mac or Ctrl+Z then Enter on Windows]
```

**Option B - From File:**
```
> file
Enter file path: my_document.txt
```

#### Step 2: Output Settings
```
Step 2: Output Settings
Output filename (output.docx): my_document.docx
Document author (Dolos): John Doe
```

#### Step 3: Timestamp Configuration
```
Step 3: Timestamp Configuration
Use custom start date? [y/n] (n): y
Start date/time (2025-01-08 14:30:00): 2024-12-01 09:00:00
```

#### Step 4: Edit Interval Settings
```
Step 4: Edit Interval Settings
Time between each sentence edit (creates randomized realistic history)
Minimum seconds between edits (30): 60
Maximum seconds between edits (300): 600
```

#### Step 5: Database Path
```
Database path (data/dolos.db): data/dolos.db
```

#### Summary & Confirmation
```
Summary:
  Text: 450 characters, 8 sentences
  Output: my_document.docx
  Author: John Doe
  Start: 2024-12-01 09:00:00
  Intervals: 60-600 seconds

Create document? [Y/n]:
```

## Multi-Line Text Input

When pasting text in interactive mode, you have **two options** to finish:

### **Option 1: Type END (Recommended)**

1. Paste or type your text (with as many line breaks as needed)
2. On a **new line**, type **END** and press Enter

**Example:**
```
Enter your text below:
You can paste multiple lines or type freely
When done, type 'END' on a new line and press Enter

This is the first sentence of my document.
This is the second sentence with important information.
This is the third and final sentence.
END
```

### **Option 2: Keyboard Shortcuts**

**Windows:**
1. Paste your text (Ctrl+V or right-click)
2. Press Enter to go to a new line
3. Press **Ctrl+Z** then **Enter** to finish

**Linux/Mac:**
1. Paste your text (Ctrl+Shift+V or Cmd+V)
2. Press Enter to go to a new line
3. Press **Ctrl+D** to finish

**Example:**
```
Enter your text below:

This is the first sentence of my document.
This is the second sentence with important information.
This is the third and final sentence.
^D  (or ^Z then Enter on Windows)
```

**Note:** The word "END" is case-insensitive (END, end, End all work)

### 2. Edit Timestamp

Modify the timestamp for a specific sentence in an existing document.

**Workflow:**

```
╭──────────────────────────────────────────╮
│ Edit Sentence Timestamp                 │
│ Modify the timestamp for a specific     │
│ sentence                                 │
╰──────────────────────────────────────────╯

Document path: my_document.docx
Database path (data/dolos.db):
```

**View Current Sentences:**
```
Current Sentences:
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃  #   ┃ Text               ┃ Timestamp           ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 0    │ First sentence.    │ 2024-12-01 09:00:00 │
│ 1    │ Second sentence.   │ 2024-12-01 09:03:45 │
│ 2    │ Third sentence.    │ 2024-12-01 09:12:30 │
└──────┴────────────────────┴─────────────────────┘

Sentence number to edit (0): 1
Current timestamp: 2024-12-01 09:03:45
New timestamp (2024-12-01 09:03:45): 2024-12-01 10:00:00

Update sentence 1 timestamp? [Y/n]:
```

### 3. Sanitize Document

Remove all metadata and track changes from a document.

**Workflow:**

```
╭──────────────────────────────────────────╮
│ Sanitize Document                        │
│ Remove all metadata and track changes    │
╰──────────────────────────────────────────╯

Document path to sanitize: sensitive.docx
Output path (leave empty to overwrite) (sensitive_clean.docx):
Use custom neutral date? [y/n] (n): y
Neutral date (2000-01-01 00:00:00):

Summary:
  Input: sensitive.docx
  Output: sensitive_clean.docx
  Neutral date: 2000-01-01 00:00:00

This will remove:
  • All track changes
  • Author information
  • Revision history
  • Application metadata

Sanitize document? [Y/n]:
```

### 4. View Metadata

Display metadata for an existing document.

**Workflow:**

```
Document path: my_document.docx
Database path (data/dolos.db):

[Displays document metadata table]
```

### 5. Quit

Exit the interactive mode.

```
What would you like to do? [create/edit/sanitize/view/quit] (create): quit
Goodbye!
```

## Multi-Line Text Input

When pasting text in interactive mode:

**Windows:**
1. Paste your text (Ctrl+V or right-click)
2. Press Enter to go to a new line
3. Press **Ctrl+Z** then **Enter** to finish

**Linux/Mac:**
1. Paste your text (Ctrl+Shift+V or Cmd+V)
2. Press Enter to go to a new line
3. Press **Ctrl+D** to finish

**Example:**
```
Enter your text (press Ctrl+D or Ctrl+Z then Enter when done):
You can paste multiple lines or type freely

This is the first sentence of my document.
This is the second sentence with important information.
This is the third and final sentence.
^D  (or ^Z on Windows)
```

## Tips for Interactive Mode

### 1. Default Values

Most prompts have sensible defaults shown in parentheses:
```
Output filename (output.docx):
```
Just press Enter to accept the default value.

### 2. Choices

When presented with choices, type one of the options:
```
How would you like to input text? [paste/file] (paste):
```
Options: `paste` or `file`. Default is `paste`.

### 3. Yes/No Prompts

```
Use custom start date? [y/n] (n):
```
- `y` or `yes` = Yes
- `n` or `no` = No
- Press Enter for default (shown in parentheses)

### 4. Number Prompts

```
Minimum seconds between edits (30): 60
```
Enter a number. Invalid input will prompt you to try again.

### 5. Timestamp Formats

Timestamps can be entered in various formats:
- `2025-01-08 14:30:00` - Full datetime
- `2025-01-08 14:30` - Without seconds
- `2025-01-08` - Date only
- `2025/01/08 14:30:00` - Alternative separator

### 6. Cancelling

During confirmation prompts, you can cancel:
```
Create document? [Y/n]: n
Cancelled
```

## Example Session: Creating a Document

Here's a complete example session:

```bash
$ dolos

╭──────────────────────────────────────────────────╮
│ Dolos - Document Metadata Manipulation Tool     │
│ Version 0.1.0                                    │
│                                                  │
│ Interactive mode - Choose your action below     │
╰──────────────────────────────────────────────────╯

What would you like to do? [create/edit/sanitize/view/quit] (create): create

╭────────────────────────────────────────────────╮
│ Create Document with Custom Edit History      │
│ Generate a Word document with fake revision   │
│ timestamps                                     │
╰────────────────────────────────────────────────╯

Step 1: Text Content
How would you like to input text? [paste/file] (paste): paste

Enter your text (press Ctrl+D or Ctrl+Z then Enter when done):
You can paste multiple lines or type freely

The quick brown fox jumps over the lazy dog. This is a test sentence.
We are creating a document with fake history. Amazing stuff!
^D

✓ Parsed 4 sentences
Preview: The quick brown fox jumps over the lazy dog...

Step 2: Output Settings
Output filename (output.docx): test_doc.docx
Document author (Dolos): Test User

Step 3: Timestamp Configuration
Use custom start date? [y/n] (n): y
Start date/time (2025-01-08 14:30:00): 2024-06-01 10:00:00

Step 4: Edit Interval Settings
Time between each sentence edit (creates randomized realistic history)
Minimum seconds between edits (30): 120
Maximum seconds between edits (300): 600

Database path (data/dolos.db):

Summary:
  Text: 142 characters, 4 sentences
  Output: test_doc.docx
  Author: Test User
  Start: 2024-06-01 10:00:00
  Intervals: 120-600 seconds

Create document? [Y/n]: y

Creating document metadata...
Building Word document...
Injecting track changes...

✓ Document created successfully!
Output: test_doc.docx
Sentences: 4
Time range: 2024-06-01 10:00:00 → 2024-06-01 10:15:43
```

## Combining Interactive and Command-Line Mode

You can mix both approaches:

**Use interactive mode for creation:**
```bash
dolos  # Interactive mode
```

**Use commands for quick operations:**
```bash
dolos view-metadata test_doc.docx
dolos sanitize test_doc.docx --output clean.docx
```

## Troubleshooting Interactive Mode

### Text Input Not Working

**Issue:** Can't enter multi-line text or Ctrl+D doesn't work.

**Solution:**
- **Windows**: Use Ctrl+Z then Enter
- **Linux/Mac**: Use Ctrl+D
- Try pressing Enter after last line before the EOF signal
- If stuck, use file input instead: choose `file` option

### Prompts Not Showing

**Issue:** Prompts appear blank or garbled.

**Solution:**
- Ensure terminal supports colors (most modern terminals do)
- Update Rich library: `pip install --upgrade rich`
- Check terminal encoding is UTF-8

### Invalid Input Errors

**Issue:** Timestamp or number prompts keep saying "Invalid input"

**Solution:**
- Check timestamp format matches examples
- For numbers, ensure you're entering digits only
- Look at the default value format for guidance

### Path Not Found

**Issue:** "Document not found" or "File not found" errors

**Solution:**
- Use absolute paths: `C:\Users\name\doc.docx` (Windows) or `/home/user/doc.docx` (Linux)
- Or use relative paths from current directory: `./documents/doc.docx`
- Check spelling and file extension

## Advanced: Scripting Interactive Input

You can pipe input to Dolos for automation:

```bash
# Create input file
cat > input.txt << EOF
create
paste
This is sentence one. This is sentence two.
EOF
test.docx
TestBot
y
2024-01-01 10:00:00
30
300
data/dolos.db
y
EOF

# Pipe to dolos
dolos < input.txt
```

However, for scripting, command-line mode is recommended:

```bash
dolos create --input-file text.txt --output test.docx --author TestBot
```

## Comparison: Interactive vs Command-Line

| Feature | Interactive Mode | Command-Line Mode |
|---------|-----------------|-------------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Beginner-friendly | ⭐⭐⭐ Requires learning syntax |
| **Speed** | ⭐⭐⭐ Step-by-step | ⭐⭐⭐⭐⭐ Fast for experts |
| **Multi-line Input** | ⭐⭐⭐⭐⭐ Easy paste | ⭐⭐⭐ File input only |
| **Scripting** | ⭐⭐ Possible but awkward | ⭐⭐⭐⭐⭐ Designed for scripts |
| **Discoverability** | ⭐⭐⭐⭐⭐ Shows all options | ⭐⭐ Need `--help` |
| **Error Recovery** | ⭐⭐⭐⭐ Re-prompt on error | ⭐⭐ Must re-run command |

**Recommendation:**
- **Learning/Exploring**: Use interactive mode
- **Automation/Scripts**: Use command-line mode
- **Quick Tasks**: Either works great!

## Getting Help

In interactive mode, all options are presented with descriptions. For command-line help:

```bash
dolos --help
dolos create --help
dolos edit-timestamp --help
```

Or read the full user guide:
```bash
cat docs/USER_GUIDE.md
```
