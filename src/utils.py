"""
Utility functions for file I/O and formatting
"""

import sys
import json
from pathlib import Path
from typing import Optional
import click
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


def read_input(file_path: Optional[str] = None) -> str:
    """
    Read input from file or stdin.

    Args:
        file_path: Path to input file. If None, reads from stdin.

    Returns:
        Content as string

    Raises:
        click.ClickException: If file cannot be read
    """
    try:
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise click.ClickException(f"File not found: {file_path}")
            return path.read_text(encoding='utf-8')
        else:
            # Read from stdin
            if sys.stdin.isatty():
                raise click.ClickException(
                    "No input provided. Use --input FILE or pipe data via stdin."
                )
            return sys.stdin.read()
    except UnicodeDecodeError:
        raise click.ClickException("File is not valid UTF-8 text")
    except Exception as e:
        raise click.ClickException(f"Error reading input: {str(e)}")


def write_output(content: str, file_path: Optional[str] = None) -> None:
    """
    Write output to file or stdout.

    Args:
        content: Content to write
        file_path: Path to output file. If None, writes to stdout.

    Raises:
        click.ClickException: If file cannot be written
    """
    try:
        if file_path:
            path = Path(file_path)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            click.secho(f"✓ Output written to: {file_path}", fg='green')
        else:
            # Write to stdout
            click.echo(content)
    except Exception as e:
        raise click.ClickException(f"Error writing output: {str(e)}")


def colorize_json(json_str: str, no_color: bool = False) -> str:
    """
    Apply syntax highlighting to JSON string.

    Args:
        json_str: JSON string to colorize
        no_color: If True, skip colorization

    Returns:
        Colorized JSON string (or original if no_color=True)
    """
    if no_color or not sys.stdout.isatty():
        return json_str

    try:
        return highlight(json_str, JsonLexer(), TerminalFormatter())
    except Exception:
        # If highlighting fails, return original
        return json_str


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
