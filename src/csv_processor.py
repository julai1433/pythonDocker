"""
CSV processing operations: convert to/from JSON
"""

import csv
import json
import io
from typing import List, Dict, Any
import click


def csv_to_json(
    csv_content: str,
    delimiter: str = ',',
    as_array: bool = True
) -> str:
    """
    Convert CSV to JSON.

    Args:
        csv_content: CSV content as string
        delimiter: CSV delimiter character
        as_array: If True, output as array. If False, output as JSON Lines

    Returns:
        JSON string

    Raises:
        click.ClickException: If CSV is invalid
    """
    try:
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
        data = list(reader)

        if not data:
            raise click.ClickException("CSV file is empty or has no data rows")

        if as_array:
            # Output as JSON array
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            # Output as JSON Lines (one object per line)
            lines = [json.dumps(row, ensure_ascii=False) for row in data]
            return '\n'.join(lines)

    except csv.Error as e:
        raise click.ClickException(f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"Error converting CSV to JSON: {str(e)}")


def json_to_csv(
    json_content: str,
    delimiter: str = ','
) -> str:
    """
    Convert JSON to CSV.

    Handles:
    - Array of objects → CSV with headers
    - Nested objects → Flattened columns (dot notation)

    Args:
        json_content: JSON content as string
        delimiter: CSV delimiter character

    Returns:
        CSV string

    Raises:
        click.ClickException: If JSON is invalid or cannot be converted
    """
    try:
        data = json.loads(json_content)

        # Ensure data is a list
        if not isinstance(data, list):
            raise click.ClickException(
                "JSON must be an array of objects. "
                f"Got: {type(data).__name__}"
            )

        if not data:
            raise click.ClickException("JSON array is empty")

        # Ensure all items are dictionaries
        if not all(isinstance(item, dict) for item in data):
            raise click.ClickException(
                "All array items must be objects/dictionaries"
            )

        # Flatten nested objects and collect all unique keys
        flattened_data = []
        all_keys = set()

        for item in data:
            flat_item = _flatten_dict(item)
            flattened_data.append(flat_item)
            all_keys.update(flat_item.keys())

        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)

        # Write CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            delimiter=delimiter,
            extrasaction='ignore'
        )

        writer.writeheader()
        writer.writerows(flattened_data)

        return output.getvalue()

    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {str(e)}")
    except Exception as e:
        if isinstance(e, click.ClickException):
            raise
        raise click.ClickException(f"Error converting JSON to CSV: {str(e)}")


def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary using dot notation.

    Example:
        {"user": {"name": "John", "age": 30}}
        → {"user.name": "John", "user.age": 30}

    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys (used in recursion)
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            # Recursively flatten nested dict
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to JSON strings (can't flatten to CSV nicely)
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        else:
            items.append((new_key, v))

    return dict(items)
