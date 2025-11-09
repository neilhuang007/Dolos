# Dolos Quick Start Guide

## ✅ Setup Complete!

Your environment is configured:
- ✅ Python 3.12.10
- ✅ pip 25.3
- ✅ Dolos 0.1.0 installed
- ✅ All dependencies installed

## 🚀 How to Run Dolos

### **Option 1: Interactive Mode (Recommended)**

Simply run:
```cmd
dolos
```

This will launch the interactive menu where you can:
1. Choose an action (create/edit/sanitize/view)
2. Follow step-by-step prompts
3. Paste multi-line text directly
4. Configure all settings interactively

**Example Interactive Session:**
```cmd
C:\Users\neil_\PycharmProjects\Dolos> dolos

╭──────────────────────────────────────────────────╮
│ Dolos - Document Metadata Manipulation Tool     │
│ Version 0.1.0                                    │
│                                                  │
│ Interactive mode - Choose your action below     │
╰──────────────────────────────────────────────────╯

What would you like to do? [create/edit/sanitize/view/quit] (create): create

Step 1: Text Content
How would you like to input text? [paste/file] (paste): paste

Enter your text (press Ctrl+Z then Enter when done):
This is the first sentence. This is the second sentence. This is the third.
^Z

✓ Parsed 3 sentences

Step 2: Output Settings
Output filename (output.docx): my_document.docx
Document author (Dolos): Government Redaction Team

Step 3: Timestamp Configuration
Use custom start date? [y/n] (n): y
Start date/time (2025-01-08 15:00:00): 2024-06-15 10:00:00

Step 4: Edit Interval Settings
Time between each sentence edit (creates randomized realistic history)
Minimum seconds between edits (30): 60
Maximum seconds between edits (300): 600

Database path (data/dolos.db):

Summary:
  Text: 87 characters, 3 sentences
  Output: my_document.docx
  Author: Government Redaction Team
  Start: 2024-06-15 10:00:00
  Intervals: 60-600 seconds

Create document? [Y/n]: y

✓ Document created successfully!
Output: my_document.docx
Sentences: 3
Time range: 2024-06-15 10:00:00 → 2024-06-15 10:15:43
```

### **Option 2: Command-Line Mode**

For quick operations:

```cmd
# Create document from text
dolos create "First sentence. Second sentence." --output test.docx

# Create from file
dolos create --input-file document.txt --output output.docx

# With custom settings
dolos create "Text here." ^
  --output doc.docx ^
  --author "John Doe" ^
  --start-date "2024-01-01 10:00:00" ^
  --min-interval 60 ^
  --max-interval 600

# View metadata
dolos view-metadata my_document.docx

# Edit timestamp
dolos edit-timestamp my_document.docx --sentence 0 --timestamp "2024-07-01 15:00:00"

# Sanitize document
dolos sanitize my_document.docx --output clean.docx
```

## 📝 Multi-Line Text Input

When using interactive mode:

1. Choose `paste` when prompted
2. Paste or type your text (with as many line breaks as needed)
3. On a new line, type **END** and press **Enter** to finish

```
Enter your text below:
You can paste multiple lines or type freely
When done, type 'END' on a new line and press Enter

First sentence here.
Second sentence here.
Third sentence here.
END
```

**Alternative:** Press **Ctrl+Z** (Windows) or **Ctrl+D** (Linux/Mac) instead of typing END

## 🎯 Common Use Cases

### Create Backdated Document
```cmd
dolos
> create
> paste
[Paste your text]
Ctrl+Z
> my_classified.docx
> Redaction Office
> y
> 2020-03-15 09:00:00
> 120
> 600
> y
```

### Sanitize Before Release
```cmd
dolos
> sanitize
> classified_draft.docx
> classified_public.docx
> n
> y
```

### View Document History
```cmd
dolos
> view
> my_document.docx
> data/dolos.db
```

## 📂 Output Files

Documents are created in the current directory unless you specify a path:
- `my_document.docx` - Your created document
- `data/dolos.db` - Metadata database

## 🔍 Viewing Results in Microsoft Word

1. Open the created `.docx` file in Microsoft Word
2. Go to **Review** tab → **Track Changes**
3. Click **Display for Review** → **All Markup**
4. Open **Reviewing Pane** to see detailed revision history
5. Hover over text to see individual timestamps for each sentence

## 📚 Full Documentation

- `README.md` - Overview and features
- `docs/USER_GUIDE.md` - Complete user guide
- `docs/INTERACTIVE_MODE.md` - Interactive mode details
- `docs/TECHNICAL.md` - Technical documentation

## 💡 Tips

1. **Use Interactive Mode** for first-time use - it guides you through everything
2. **Use Command-Line Mode** for scripting and automation
3. **Test with short text** first to understand the workflow
4. **Check the database** to see all your document metadata
5. **Sanitize documents** before releasing to remove all traces

## ❓ Need Help?

```cmd
# General help
dolos --help

# Command-specific help
dolos create --help
dolos edit-timestamp --help
dolos sanitize --help
dolos view-metadata --help
```

## 🎉 You're Ready!

Just run `dolos` and start creating documents with custom edit histories!
