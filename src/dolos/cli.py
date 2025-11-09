"""Command-line interface for Dolos."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich import print as rprint

from . import __version__
from .text_parser import split_into_sentences
from .metadata_manager import MetadataManager
from .document_builder import DocumentBuilder
from .xml_injector import TrackChangesInjector
from .sanitizer import DocumentSanitizer
from .metadata_editor import MetadataEditor
from .utils import parse_timestamp, ensure_directory

# Initialize Typer app
app = typer.Typer(
    name="dolos",
    help="Word document metadata manipulation tool",
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False
)

# Rich console for beautiful output
console = Console()


@app.command()
def create(
    text: Optional[str] = typer.Argument(None, help="Text content for the document"),
    input_file: Optional[Path] = typer.Option(None, "--input-file", "-f", help="Read text from file"),
    output: Path = typer.Option("output.docx", "--output", "-o", help="Output DOCX file path"),
    author: str = typer.Option("Dolos", "--author", "-a", help="Document author name"),
    start_date: Optional[str] = typer.Option(None, "--start-date", "-s", help="Start timestamp (YYYY-MM-DD HH:MM:SS)"),
    min_interval: int = typer.Option(30, "--min-interval", help="Minimum seconds between edits"),
    max_interval: int = typer.Option(300, "--max-interval", help="Maximum seconds between edits"),
    no_track_changes: bool = typer.Option(False, "--no-track-changes", help="Create clean document without any track changes metadata"),
    accept_all_changes: bool = typer.Option(False, "--accept-all-changes", help="Keep timestamps but show text as final (not suggestions)"),
    title: Optional[str] = typer.Option(None, "--title", help="Document title"),
    subject: Optional[str] = typer.Option(None, "--subject", help="Document subject"),
    keywords: Optional[str] = typer.Option(None, "--keywords", help="Document keywords"),
    comments: Optional[str] = typer.Option(None, "--comments", help="Document comments"),
    total_edit_time: Optional[int] = typer.Option(None, "--total-edit-time", help="Total editing time in minutes"),
    db_path: str = typer.Option("data/dolos.db", "--db", help="Database path"),
):
    """Create a Word document with fake edit history.

    Examples:
        dolos create "Hello world. This is a test." -o test.docx
        dolos create --input-file text.txt -o output.docx
        dolos create "Sample text." --start-date "2025-01-01 10:00:00"
    """
    try:
        # Get text content
        if text is None and input_file is None:
            console.print("[red]Error:[/red] Must provide either text argument or --input-file", style="bold")
            sys.exit(1)

        if input_file:
            if not input_file.exists():
                console.print(f"[red]Error:[/red] File not found: {input_file}", style="bold")
                sys.exit(1)
            text = input_file.read_text(encoding='utf-8')

        if not text or not text.strip():
            console.print("[red]Error:[/red] Text content is empty", style="bold")
            sys.exit(1)

        # Parse timestamp
        start_timestamp = None
        if start_date:
            try:
                start_timestamp = parse_timestamp(start_date)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}", style="bold")
                sys.exit(1)

        # Parse sentences
        console.print(f"[cyan]Parsing text into sentences...[/cyan]")
        sentences = split_into_sentences(text)
        console.print(f"[green]>[/green] Found {len(sentences)} sentences")

        # Initialize managers
        ensure_directory(Path(db_path).parent)
        metadata_mgr = MetadataManager(db_path)
        doc_builder = DocumentBuilder()
        track_injector = TrackChangesInjector()

        # Create document in database
        console.print(f"[cyan]Creating document metadata...[/cyan]")
        doc = metadata_mgr.create_document(
            filename=str(output),
            sentences=sentences,
            start_timestamp=start_timestamp,
            min_interval_seconds=min_interval,
            max_interval_seconds=max_interval,
            author=author
        )
        console.print(f"[green]>[/green] Metadata stored in database")

        # Build DOCX
        console.print(f"[cyan]Building Word document...[/cyan]")
        temp_path = str(output) + ".tmp"
        doc_builder.create_document(
            sentences=doc.sentences,
            output_path=temp_path,
            author=author,
            title=title,
            subject=subject,
            keywords=keywords,
            comments=comments,
            total_edit_minutes=total_edit_time
        )

        if no_track_changes:
            # Just use the clean document without track changes
            console.print(f"[cyan]Creating clean document (no track changes)...[/cyan]")
            Path(temp_path).rename(output)
        elif accept_all_changes:
            # Keep timestamps but show final text (not as suggestions)
            console.print(f"[cyan]Creating document with timestamps (final text, not suggestions)...[/cyan]")
            track_injector.inject_track_changes(
                docx_path=temp_path,
                sentences=doc.sentences,
                output_path=str(output),
                accept_changes=True
            )
            Path(temp_path).unlink(missing_ok=True)
        else:
            # Inject track changes (shows as suggestions)
            console.print(f"[cyan]Injecting track changes (will show as suggestions)...[/cyan]")
            track_injector.inject_track_changes(
                docx_path=temp_path,
                sentences=doc.sentences,
                output_path=str(output),
                accept_changes=False
            )
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

        # Set total editing time if specified
        if total_edit_time and total_edit_time > 0:
            console.print(f"[cyan]Setting total editing time...[/cyan]")
            MetadataEditor.set_total_edit_time(str(output), total_edit_time)

        console.print(f"\n[bold green]OK Document created successfully![/bold green]")
        console.print(f"[dim]Output:[/dim] {output}")
        console.print(f"[dim]Sentences:[/dim] {len(sentences)}")
        console.print(f"[dim]Time range:[/dim] {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')} -> {doc.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="bold")
        sys.exit(1)


@app.command()
def edit_timestamp(
    document: Path = typer.Argument(..., help="DOCX file to edit"),
    sentence: int = typer.Option(..., "--sentence", "-n", help="Sentence number (0-indexed)"),
    timestamp: str = typer.Option(..., "--timestamp", "-t", help="New timestamp (YYYY-MM-DD HH:MM:SS)"),
    db_path: str = typer.Option("data/dolos.db", "--db", help="Database path"),
):
    """Edit timestamp for a specific sentence.

    Example:
        dolos edit-timestamp document.docx --sentence 0 --timestamp "2025-01-15 14:30:00"
    """
    try:
        if not document.exists():
            console.print(f"[red]Error:[/red] Document not found: {document}", style="bold")
            sys.exit(1)

        # Parse new timestamp
        try:
            new_timestamp = parse_timestamp(timestamp)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}", style="bold")
            sys.exit(1)

        # Update metadata
        metadata_mgr = MetadataManager(db_path)
        success = metadata_mgr.update_sentence_timestamp(
            document_filename=str(document),
            sentence_position=sentence,
            new_timestamp=new_timestamp
        )

        if not success:
            console.print(f"[red]Error:[/red] Could not update sentence {sentence}", style="bold")
            sys.exit(1)

        # Rebuild document with new timestamps
        console.print(f"[cyan]Rebuilding document with new timestamp...[/cyan]")
        doc = metadata_mgr.get_document_by_filename(str(document))

        if doc:
            doc_builder = DocumentBuilder()
            track_injector = TrackChangesInjector()

            temp_path = str(document) + ".tmp"
            doc_builder.create_document(
                sentences=doc.sentences,
                output_path=temp_path,
                author=doc.author
            )

            track_injector.inject_track_changes(
                docx_path=temp_path,
                sentences=doc.sentences,
                output_path=str(document)
            )

            Path(temp_path).unlink(missing_ok=True)

        console.print(f"[bold green]SUCCESS: Timestamp updated successfully![/bold green]")
        console.print(f"[dim]Sentence {sentence}:[/dim] {new_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="bold")
        sys.exit(1)


@app.command()
def view_metadata(
    document: Path = typer.Argument(..., help="DOCX file to view metadata"),
    db_path: str = typer.Option("data/dolos.db", "--db", help="Database path"),
    export_json: Optional[Path] = typer.Option(None, "--json", help="Export to JSON file"),
):
    """View metadata for a document.

    Example:
        dolos view-metadata document.docx
        dolos view-metadata document.docx --json metadata.json
    """
    try:
        if not document.exists():
            console.print(f"[red]Error:[/red] Document not found: {document}", style="bold")
            sys.exit(1)

        metadata_mgr = MetadataManager(db_path)
        metadata = metadata_mgr.get_document_metadata(str(document))

        if not metadata:
            console.print(f"[yellow]Warning:[/yellow] No metadata found for {document}", style="bold")
            sys.exit(0)

        # Export to JSON if requested
        if export_json:
            with open(export_json, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            console.print(f"[green]>[/green] Metadata exported to {export_json}")

        # Display in terminal
        console.print(f"\n[bold cyan]Document Metadata[/bold cyan]")
        console.print(f"[dim]Filename:[/dim] {metadata['filename']}")
        console.print(f"[dim]Author:[/dim] {metadata['author']}")
        console.print(f"[dim]Created:[/dim] {metadata['created_at']}")
        console.print(f"[dim]Modified:[/dim] {metadata['last_modified']}")
        console.print(f"[dim]Sentences:[/dim] {metadata['sentence_count']}")

        # Create table for sentences
        table = Table(title="\nSentence Details", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=6)
        table.add_column("Text", min_width=30)
        table.add_column("Created", style="cyan")
        table.add_column("Modified", style="green")

        for sent in metadata['sentences']:
            text_preview = sent['text'][:50] + "..." if len(sent['text']) > 50 else sent['text']
            table.add_row(
                str(sent['position']),
                text_preview,
                sent['created'],
                sent['modified']
            )

        console.print(table)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="bold")
        sys.exit(1)


@app.command()
def sanitize(
    document: Path = typer.Argument(..., help="DOCX file to sanitize"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path (default: overwrites input)"),
    keep_content: bool = typer.Option(True, "--keep-content", help="Keep document content"),
    neutral_date: Optional[str] = typer.Option(None, "--neutral-date", help="Neutral timestamp to use"),
):
    """Remove all metadata and track changes from a document.

    Example:
        dolos sanitize document.docx --output clean.docx
        dolos sanitize document.docx --neutral-date "2000-01-01 00:00:00"
    """
    try:
        if not document.exists():
            console.print(f"[red]Error:[/red] Document not found: {document}", style="bold")
            sys.exit(1)

        output_path = output if output else document

        # Parse neutral date
        neutral_timestamp = None
        if neutral_date:
            try:
                neutral_timestamp = parse_timestamp(neutral_date)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}", style="bold")
                sys.exit(1)

        console.print(f"[cyan]Sanitizing document...[/cyan]")
        sanitizer = DocumentSanitizer()
        sanitizer.sanitize_document(
            input_path=str(document),
            output_path=str(output_path),
            remove_track_changes=True,
            remove_metadata=True,
            neutral_timestamp=neutral_timestamp
        )

        console.print(f"\n[bold green]OK Document sanitized successfully![/bold green]")
        console.print(f"[dim]Output:[/dim] {output_path}")
        console.print(f"[dim]Removed:[/dim] Track changes, metadata, revision history")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="bold")
        sys.exit(1)


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold cyan]Dolos[/bold cyan] version [green]{__version__}[/green]")


def get_multiline_input() -> str:
    """Get multi-line text input from user."""
    console.print("\n[cyan]Enter your text below:[/cyan]")
    console.print("[dim]You can paste multiple lines or type freely[/dim]")
    console.print("[yellow]When done, type 'END' on a new line and press Enter[/yellow]\n")

    lines = []
    while True:
        try:
            line = input()
            # Check if user typed END to finish
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            # Handle Ctrl+D / Ctrl+Z
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            console.print("\n[yellow]Input cancelled[/yellow]")
            return ""

    return "\n".join(lines)


def interactive_create():
    """Interactive mode for creating documents."""
    console.print(Panel.fit(
        "[bold cyan]Create Document with Custom Edit History[/bold cyan]\n"
        "Generate a Word document with fake revision timestamps",
        border_style="cyan"
    ))

    # Get text content
    console.print("\n[bold]Step 1: Text Content[/bold]")
    choice = Prompt.ask(
        "How would you like to input text?",
        choices=["paste", "file"],
        default="paste"
    )

    text = None
    if choice == "paste":
        text = get_multiline_input()
    else:
        file_path = Prompt.ask("Enter file path")
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            return
        text = path.read_text(encoding='utf-8')

    if not text or not text.strip():
        console.print("[red]Error:[/red] No text provided")
        return

    # Parse sentences preview
    sentences = split_into_sentences(text)
    console.print(f"\n[green]>[/green] Parsed {len(sentences)} sentences")
    console.print(f"[dim]Preview: {sentences[0][:60]}...[/dim]" if sentences else "")

    # Get output path
    console.print("\n[bold]Step 2: Output Settings[/bold]")
    output_path = Prompt.ask("Output filename", default="output.docx")
    author = Prompt.ask("Document author", default="Dolos")

    # Get timestamp settings
    console.print("\n[bold]Step 3: Timestamp Configuration[/bold]")
    use_custom_start = Confirm.ask("Use custom start date?", default=False)

    start_timestamp = None
    if use_custom_start:
        start_date_str = Prompt.ask(
            "Start date/time",
            default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        try:
            start_timestamp = parse_timestamp(start_date_str)
        except ValueError as e:
            console.print(f"[yellow]Warning:[/yellow] Invalid date format, using current time")
            start_timestamp = None

    # Get interval settings
    console.print("\n[bold]Step 4: Edit Interval Settings[/bold]")
    console.print("[dim]Time between each sentence edit (creates randomized realistic history)[/dim]")

    min_interval = IntPrompt.ask("Minimum seconds between edits", default=30)
    max_interval = IntPrompt.ask("Maximum seconds between edits", default=300)

    if min_interval > max_interval:
        console.print("[yellow]Warning:[/yellow] Min > Max, swapping values")
        min_interval, max_interval = max_interval, min_interval

    # Document metadata
    console.print("\n[bold]Step 5: Document Metadata (Optional)[/bold]")
    add_metadata = Confirm.ask("Add document metadata (title, keywords, etc.)?", default=False)

    title = None
    subject = None
    keywords = None
    comments = None
    total_edit_time = None

    if add_metadata:
        title = Prompt.ask("Document title", default="")
        subject = Prompt.ask("Document subject", default="")
        keywords = Prompt.ask("Keywords/tags", default="")
        comments = Prompt.ask("Comments", default="")
        total_edit_time = IntPrompt.ask("Total editing time (minutes)", default=0)

        # Convert empty strings to None
        title = title if title else None
        subject = subject if subject else None
        keywords = keywords if keywords else None
        comments = comments if comments else None
        total_edit_time = total_edit_time if total_edit_time > 0 else None

    # Track changes option
    console.print("\n[bold]Step 6: Document Mode[/bold]")
    console.print("[dim]Choose how the document should appear in Word:[/dim]")

    doc_mode = Prompt.ask(
        "Document mode",
        choices=["final", "suggestions", "clean"],
        default="final"
    )

    console.print(f"\n[dim]Selected: {doc_mode}[/dim]")
    if doc_mode == "final":
        console.print("[dim]  -> Text appears final with timestamps (RECOMMENDED)[/dim]")
    elif doc_mode == "suggestions":
        console.print("[dim]  -> Text appears as track change suggestions with popups[/dim]")
    else:
        console.print("[dim]  -> Clean document, no track changes or timestamps[/dim]")

    no_track_changes = (doc_mode == "clean")
    accept_all_changes = (doc_mode == "final")

    # Get database path
    db_path = Prompt.ask("Database path", default="data/dolos.db")

    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Text: {len(text)} characters, {len(sentences)} sentences")
    console.print(f"  Output: {output_path}")
    console.print(f"  Author: {author}")
    console.print(f"  Start: {start_timestamp or 'Current time'}")
    console.print(f"  Intervals: {min_interval}-{max_interval} seconds")

    if no_track_changes:
        console.print(f"  Mode: Clean document (no timestamps)")
    elif accept_all_changes:
        console.print(f"  Mode: Final text with timestamps")
    else:
        console.print(f"  Mode: Track changes (suggestions)")

    if title:
        console.print(f"  Title: {title}")
    if total_edit_time:
        console.print(f"  Total edit time: {total_edit_time} minutes")

    # Confirm
    if not Confirm.ask("\n[bold]Create document?[/bold]", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Create document
    try:
        ensure_directory(Path(db_path).parent)
        metadata_mgr = MetadataManager(db_path)
        doc_builder = DocumentBuilder()
        track_injector = TrackChangesInjector()

        console.print("\n[cyan]Creating document metadata...[/cyan]")
        doc = metadata_mgr.create_document(
            filename=output_path,
            sentences=sentences,
            start_timestamp=start_timestamp,
            min_interval_seconds=min_interval,
            max_interval_seconds=max_interval,
            author=author
        )

        console.print(f"[cyan]Building Word document...[/cyan]")
        temp_path = str(output_path) + ".tmp"
        doc_builder.create_document(
            sentences=doc.sentences,
            output_path=temp_path,
            author=author,
            title=title,
            subject=subject,
            keywords=keywords,
            comments=comments,
            total_edit_minutes=total_edit_time
        )

        if no_track_changes:
            console.print(f"[cyan]Creating clean document (no track changes)...[/cyan]")
            Path(temp_path).rename(output_path)
        elif accept_all_changes:
            console.print(f"[cyan]Creating document with timestamps (final text)...[/cyan]")
            track_injector.inject_track_changes(
                docx_path=temp_path,
                sentences=doc.sentences,
                output_path=output_path,
                accept_changes=True
            )
            Path(temp_path).unlink(missing_ok=True)
        else:
            console.print(f"[cyan]Injecting track changes (suggestions)...[/cyan]")
            track_injector.inject_track_changes(
                docx_path=temp_path,
                sentences=doc.sentences,
                output_path=output_path,
                accept_changes=False
            )
            Path(temp_path).unlink(missing_ok=True)

        # Set total editing time if specified
        if total_edit_time and total_edit_time > 0:
            console.print(f"[cyan]Setting total editing time...[/cyan]")
            MetadataEditor.set_total_edit_time(output_path, total_edit_time)

        console.print(f"\n[bold green]SUCCESS: Document created successfully![/bold green]")
        console.print(f"[dim]Output:[/dim] {output_path}")
        console.print(f"[dim]Sentences:[/dim] {len(sentences)}")
        console.print(f"[dim]Time range:[/dim] {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')} -> {doc.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")


def interactive_edit():
    """Interactive mode for editing timestamps."""
    console.print(Panel.fit(
        "[bold cyan]Edit Sentence Timestamp[/bold cyan]\n"
        "Modify the timestamp for a specific sentence",
        border_style="cyan"
    ))

    document_path = Prompt.ask("\nDocument path")

    if not Path(document_path).exists():
        console.print(f"[red]Error:[/red] Document not found: {document_path}")
        return

    # Show current metadata
    db_path = Prompt.ask("Database path", default="data/dolos.db")
    metadata_mgr = MetadataManager(db_path)
    metadata = metadata_mgr.get_document_metadata(document_path)

    if not metadata:
        console.print(f"[yellow]Warning:[/yellow] No metadata found for this document")
        return

    # Display sentences
    console.print(f"\n[bold]Current Sentences:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=6)
    table.add_column("Text", min_width=30)
    table.add_column("Timestamp", style="cyan")

    for sent in metadata['sentences']:
        text_preview = sent['text'][:50] + "..." if len(sent['text']) > 50 else sent['text']
        table.add_row(
            str(sent['position']),
            text_preview,
            sent['modified']
        )

    console.print(table)

    # Get sentence to edit
    sentence_num = IntPrompt.ask(
        "\nSentence number to edit",
        default=0
    )

    if sentence_num < 0 or sentence_num >= len(metadata['sentences']):
        console.print(f"[red]Error:[/red] Invalid sentence number")
        return

    # Get new timestamp
    current_timestamp = metadata['sentences'][sentence_num]['modified']
    console.print(f"\n[dim]Current timestamp:[/dim] {current_timestamp}")

    new_timestamp_str = Prompt.ask(
        "New timestamp",
        default=current_timestamp
    )

    try:
        new_timestamp = parse_timestamp(new_timestamp_str)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # Confirm
    if not Confirm.ask(f"\nUpdate sentence {sentence_num} timestamp?", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Update
    try:
        console.print("\n[cyan]Updating timestamp...[/cyan]")
        success = metadata_mgr.update_sentence_timestamp(
            document_filename=document_path,
            sentence_position=sentence_num,
            new_timestamp=new_timestamp
        )

        if not success:
            console.print(f"[red]Error:[/red] Could not update timestamp")
            return

        console.print(f"[cyan]Rebuilding document...[/cyan]")
        doc = metadata_mgr.get_document_by_filename(document_path)
        doc_builder = DocumentBuilder()
        track_injector = TrackChangesInjector()

        temp_path = str(document_path) + ".tmp"
        doc_builder.create_document(
            sentences=doc.sentences,
            output_path=temp_path,
            author=doc.author
        )

        track_injector.inject_track_changes(
            docx_path=temp_path,
            sentences=doc.sentences,
            output_path=document_path
        )

        Path(temp_path).unlink(missing_ok=True)

        console.print(f"\n[bold green]SUCCESS: Timestamp updated successfully![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")


def interactive_sanitize():
    """Interactive mode for sanitizing documents."""
    console.print(Panel.fit(
        "[bold cyan]Sanitize Document[/bold cyan]\n"
        "Remove all metadata and track changes",
        border_style="cyan"
    ))

    document_path = Prompt.ask("\nDocument path to sanitize")

    if not Path(document_path).exists():
        console.print(f"[red]Error:[/red] Document not found: {document_path}")
        return

    # Output path
    default_output = str(Path(document_path).stem) + "_clean.docx"
    output_path = Prompt.ask("Output path (leave empty to overwrite)", default=default_output)

    # Neutral date
    use_neutral = Confirm.ask("Use custom neutral date?", default=False)
    neutral_timestamp = None

    if use_neutral:
        neutral_str = Prompt.ask("Neutral date", default="2000-01-01 00:00:00")
        try:
            neutral_timestamp = parse_timestamp(neutral_str)
        except ValueError:
            console.print("[yellow]Warning:[/yellow] Invalid date, using default")

    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Input: {document_path}")
    console.print(f"  Output: {output_path}")
    console.print(f"  Neutral date: {neutral_timestamp or '2000-01-01 00:00:00'}")
    console.print("\n[yellow]This will remove:[/yellow]")
    console.print("  • All track changes")
    console.print("  • Author information")
    console.print("  • Revision history")
    console.print("  • Application metadata")

    if not Confirm.ask("\n[bold]Sanitize document?[/bold]", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        console.print("\n[cyan]Sanitizing document...[/cyan]")
        sanitizer = DocumentSanitizer()
        sanitizer.sanitize_document(
            input_path=document_path,
            output_path=output_path,
            remove_track_changes=True,
            remove_metadata=True,
            neutral_timestamp=neutral_timestamp
        )

        console.print(f"\n[bold green]OK Document sanitized successfully![/bold green]")
        console.print(f"[dim]Output:[/dim] {output_path}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Dolos - Word document metadata manipulation tool.

    Run without arguments for interactive mode, or use specific commands.
    """
    # If no command provided, run interactive mode
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold cyan]Dolos - Document Metadata Manipulation Tool[/bold cyan]\n"
            f"Version {__version__}\n\n"
            "Interactive mode - Choose your action below",
            border_style="cyan"
        ))

        action = Prompt.ask(
            "\nWhat would you like to do?",
            choices=["create", "edit", "sanitize", "view", "quit"],
            default="create"
        )

        if action == "create":
            interactive_create()
        elif action == "edit":
            interactive_edit()
        elif action == "sanitize":
            interactive_sanitize()
        elif action == "view":
            # Quick view
            document_path = Prompt.ask("Document path")
            if Path(document_path).exists():
                db_path = Prompt.ask("Database path", default="data/dolos.db")
                ctx.invoke(view_metadata, document=Path(document_path), db_path=db_path)
            else:
                console.print(f"[red]Error:[/red] Document not found")
        elif action == "quit":
            console.print("[dim]Goodbye![/dim]")
            return


if __name__ == "__main__":
    app()
