"""
JSON processing operations: prettify, minify, validate
"""

import json
from typing import Any, Dict
import click


def prettify(
    input_str: str,
    indent: int = 2,
    sort_keys: bool = False
) -> str:
    """
    Pretty-print JSON with formatting.

    Args:
        input_str: Raw JSON string
        indent: Number of spaces for indentation
        sort_keys: Whether to sort object keys alphabetically

    Returns:
        Formatted JSON string

    Raises:
        click.ClickException: If JSON is invalid
    """
    try:
        data = json.loads(input_str)
        return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {str(e)}")


def minify(input_str: str) -> str:
    """
    Minify JSON by removing all unnecessary whitespace.

    Args:
        input_str: JSON string (formatted or not)

    Returns:
        Minified JSON string

    Raises:
        click.ClickException: If JSON is invalid
    """
    try:
        data = json.loads(input_str)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {str(e)}")


def validate(input_str: str) -> Dict[str, Any]:
    """
    Validate JSON and return metadata.

    Args:
        input_str: JSON string to validate

    Returns:
        Dictionary with validation results and metadata

    Raises:
        click.ClickException: If JSON is invalid
    """
    try:
        data = json.loads(input_str)

        # Determine top-level type
        if isinstance(data, dict):
            data_type = "object"
            item_count = len(data)
            item_label = "keys"
        elif isinstance(data, list):
            data_type = "array"
            item_count = len(data)
            item_label = "items"
        else:
            data_type = type(data).__name__
            item_count = None
            item_label = None

        return {
            "valid": True,
            "type": data_type,
            "item_count": item_count,
            "item_label": item_label,
            "lines": len(input_str.splitlines()),
            "size": len(input_str.encode('utf-8')),
        }
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
