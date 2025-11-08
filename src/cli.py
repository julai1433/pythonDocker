"""
Main CLI interface using Click framework

This demonstrates the Command Pattern - each command is a separate function.
"""

import click
from . import __version__
from . import json_processor
from . import csv_processor
from . import utils


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    JSON/CSV Transformer - A Docker-based CLI tool

    Transform and format JSON and CSV data with ease.

    Examples:

        # Pretty-print JSON from stdin
        echo '{"name":"John"}' | docker run -i jsonify prettify

        # Minify JSON file
        docker run -v $(pwd):/data jsonify minify -i /data/config.json

        # Convert CSV to JSON
        docker run -v $(pwd):/data jsonify csv-to-json -i /data/users.csv
    """
    pass


@cli.command()
@click.option(
    '-i', '--input',
    type=click.Path(),
    help='Input file path (if not provided, reads from stdin)'
)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output file path (if not provided, writes to stdout)'
)
@click.option(
    '--indent',
    type=int,
    default=2,
    help='Indentation spaces (default: 2)'
)
@click.option(
    '--sort-keys',
    is_flag=True,
    help='Sort object keys alphabetically'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Disable syntax highlighting'
)
def prettify(input, output, indent, sort_keys, no_color):
    """
    Pretty-print JSON with formatting and optional syntax highlighting.

    Examples:

        # From stdin
        echo '{"a":1,"b":2}' | docker run -i jsonify prettify

        # From file
        docker run -v $(pwd):/data jsonify prettify -i /data/raw.json

        # Custom indentation and sorted keys
        docker run -v $(pwd):/data jsonify prettify -i /data/data.json --indent 4 --sort-keys
    """
    try:
        # Read input
        input_content = utils.read_input(input)

        # Process
        formatted = json_processor.prettify(input_content, indent, sort_keys)

        # Colorize if outputting to terminal
        if not output:
            formatted = utils.colorize_json(formatted, no_color)

        # Write output
        utils.write_output(formatted, output)

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
@click.option(
    '-i', '--input',
    type=click.Path(),
    help='Input file path (if not provided, reads from stdin)'
)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output file path (if not provided, writes to stdout)'
)
def minify(input, output):
    """
    Minify JSON by removing all whitespace.

    Useful for reducing file size or preparing data for APIs.

    Examples:

        # From stdin
        cat pretty.json | docker run -i jsonify minify

        # From file to file
        docker run -v $(pwd):/data jsonify minify -i /data/input.json -o /data/output.json
    """
    try:
        # Read input
        input_content = utils.read_input(input)

        # Process
        minified = json_processor.minify(input_content)

        # Write output
        utils.write_output(minified, output)

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
@click.option(
    '-i', '--input',
    type=click.Path(),
    help='Input file path (if not provided, reads from stdin)'
)
def validate(input):
    """
    Validate JSON and display metadata.

    Checks if JSON is valid and shows information about the structure.

    Examples:

        # Validate from stdin
        cat data.json | docker run -i jsonify validate

        # Validate file
        docker run -v $(pwd):/data jsonify validate -i /data/response.json
    """
    try:
        # Read input
        input_content = utils.read_input(input)

        # Validate and get metadata
        result = json_processor.validate(input_content)

        # Display results
        click.secho("✓ Valid JSON", fg='green', bold=True)
        click.echo(f"  Type: {result['type']}")

        if result['item_count'] is not None:
            click.echo(f"  {result['item_label'].capitalize()}: {result['item_count']}")

        click.echo(f"  Lines: {result['lines']}")
        click.echo(f"  Size: {utils.format_file_size(result['size'])}")

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
@click.option(
    '-i', '--input',
    required=True,
    type=click.Path(),
    help='Input CSV file path'
)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output JSON file path (if not provided, writes to stdout)'
)
@click.option(
    '--delimiter',
    default=',',
    help='CSV delimiter (default: comma)'
)
@click.option(
    '--lines',
    is_flag=True,
    help='Output as JSON Lines instead of array'
)
def csv_to_json(input, output, delimiter, lines):
    """
    Convert CSV file to JSON.

    Reads CSV with headers and converts to JSON array of objects.

    Examples:

        # Convert to JSON array
        docker run -v $(pwd):/data jsonify csv-to-json -i /data/users.csv

        # Save to file
        docker run -v $(pwd):/data jsonify csv-to-json -i /data/users.csv -o /data/users.json

        # Output as JSON Lines (one object per line)
        docker run -v $(pwd):/data jsonify csv-to-json -i /data/users.csv --lines
    """
    try:
        # Read input (CSV requires file input, not stdin for this command)
        csv_content = utils.read_input(input)

        # Process
        json_output = csv_processor.csv_to_json(
            csv_content,
            delimiter=delimiter,
            as_array=not lines
        )

        # Write output
        utils.write_output(json_output, output)

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
@click.option(
    '-i', '--input',
    type=click.Path(),
    help='Input JSON file path (if not provided, reads from stdin)'
)
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output CSV file path (if not provided, writes to stdout)'
)
@click.option(
    '--delimiter',
    default=',',
    help='CSV delimiter (default: comma)'
)
def json_to_csv(input, output, delimiter):
    """
    Convert JSON array to CSV.

    Expects a JSON array of objects. Nested objects are flattened using dot notation.

    Examples:

        # From stdin
        echo '[{"name":"Alice","age":25}]' | docker run -i jsonify json-to-csv

        # From file
        docker run -v $(pwd):/data jsonify json-to-csv -i /data/users.json -o /data/users.csv
    """
    try:
        # Read input
        json_content = utils.read_input(input)

        # Process
        csv_output = csv_processor.json_to_csv(json_content, delimiter=delimiter)

        # Write output
        utils.write_output(csv_output, output)

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command()
def info():
    """
    Display information about this tool and Docker usage.
    """
    click.secho("JSON/CSV Transformer", fg='cyan', bold=True)
    click.echo(f"Version: {__version__}")
    click.echo()
    click.secho("Docker Usage Examples:", fg='yellow', bold=True)
    click.echo()
    click.echo("  # Run with stdin/stdout")
    click.echo("  echo '{\"a\":1}' | docker run -i jsonify prettify")
    click.echo()
    click.echo("  # Mount volume to process files")
    click.echo("  docker run -v $(pwd)/data:/data jsonify prettify -i /data/file.json")
    click.echo()
    click.echo("  # Chain commands (prettify then validate)")
    click.echo("  cat data.json | docker run -i jsonify prettify | docker run -i jsonify validate")
    click.echo()
    click.secho("Available Commands:", fg='yellow', bold=True)
    click.echo("  prettify      - Format JSON beautifully")
    click.echo("  minify        - Remove all whitespace from JSON")
    click.echo("  validate      - Check JSON validity and show metadata")
    click.echo("  csv-to-json   - Convert CSV to JSON")
    click.echo("  json-to-csv   - Convert JSON to CSV")
    click.echo()
    click.echo("Run 'docker run jsonify COMMAND --help' for command-specific help")


# This is the entry point when running: python -m src.cli
if __name__ == '__main__':
    cli()
