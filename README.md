# JSON/CSV Transformer - Docker Learning Project

A production-quality CLI tool for transforming JSON and CSV data, built to learn Docker best practices.

## What This Project Teaches

- **Docker fundamentals**: Images, containers, layers, caching
- **Multi-stage builds**: Creating lean production images
- **Volume mounting**: Processing files from your host machine
- **Security best practices**: Non-root users, read-only volumes
- **Dockerfile optimization**: Layer caching, .dockerignore
- **Real-world patterns**: stdin/stdout, debugging containers

## Features

- **Pretty-print JSON** with syntax highlighting
- **Minify JSON** to remove whitespace
- **Validate JSON** with detailed metadata
- **Convert CSV to JSON** (and vice versa)
- **Flatten nested JSON** when converting to CSV
- **Pipeline-friendly** (works with stdin/stdout)

## Quick Start

### 1. Build the Image

```bash
docker build -t jsonify .
```

**What this does:**
- Creates a Docker image named "jsonify"
- Uses multi-stage build (builder + runtime)
- Installs Python dependencies
- Final image: ~225MB

### 2. Basic Usage

```bash
# Show help
docker run --rm jsonify

# Show version
docker run --rm jsonify --version

# Get command help
docker run --rm jsonify prettify --help
```

## Usage Examples

### Pretty-Print JSON

**From stdin:**
```bash
echo '{"name":"John","age":30}' | docker run -i --rm jsonify prettify
```

**From file:**
```bash
docker run --rm -v $(pwd)/examples:/data jsonify prettify -i /data/sample.json
```

**With options:**
```bash
# 4-space indent + sorted keys
echo '{"b":2,"a":1}' | docker run -i --rm jsonify prettify --indent 4 --sort-keys

# Save to file
docker run --rm -v $(pwd):/data jsonify prettify -i /data/input.json -o /data/output.json
```

### Minify JSON

```bash
# Remove all whitespace
cat pretty.json | docker run -i --rm jsonify minify

# From/to files
docker run --rm -v $(pwd):/data jsonify minify -i /data/input.json -o /data/output.json
```

### Validate JSON

```bash
# Check if valid + show metadata
cat data.json | docker run -i --rm jsonify validate

# Validate file
docker run --rm -v $(pwd):/data jsonify validate -i /data/response.json
```

**Output example:**
```
✓ Valid JSON
  Type: object
  Keys: 5
  Lines: 12
  Size: 1.2 KB
```

### CSV to JSON

```bash
# Convert CSV to JSON array
docker run --rm -v $(pwd)/examples:/data jsonify csv-to-json -i /data/users.csv

# Save to file
docker run --rm -v $(pwd)/examples:/data jsonify csv-to-json \
  -i /data/users.csv -o /data/users.json

# Output as JSON Lines (one object per line)
docker run --rm -v $(pwd)/examples:/data jsonify csv-to-json \
  -i /data/users.csv --lines
```

### JSON to CSV

```bash
# Convert JSON array to CSV
echo '[{"name":"Alice","age":25}]' | docker run -i --rm jsonify json-to-csv

# From/to files
docker run --rm -v $(pwd):/data jsonify json-to-csv \
  -i /data/users.json -o /data/users.csv

# Nested objects are flattened:
# {"user": {"name": "John"}} → user.name,John
```

## Docker Concepts Demonstrated

### 1. Volume Mounting

Mount your local files into the container:

```bash
# Mount current directory as /data in container
docker run --rm -v $(pwd):/data jsonify prettify -i /data/file.json
                    └─┬─┘       └─┬─┘
                      │           └─ Path inside container
                      └─────────── Path on your Mac

# Read-only mount (security)
docker run --rm -v $(pwd)/examples:/data:ro jsonify validate -i /data/file.json
                                          └─┬─┘
                                            └─ Read-only flag
```

**Why this matters:**
- Process files on your Mac without copying them
- Changes persist after container stops
- Read-only prevents accidental modifications

### 2. stdin/stdout (Unix Philosophy)

Use containers as pipeline components:

```bash
# Chain commands
cat file.json | docker run -i --rm jsonify prettify | docker run -i --rm jsonify minify

# Combine with other Unix tools
curl https://api.github.com/users/octocat | docker run -i --rm jsonify prettify | less

# The -i flag keeps stdin open
# The --rm flag auto-removes container after exit
```

### 3. Multi-Stage Builds

Check the `Dockerfile` to see:

```dockerfile
# Stage 1: Builder (includes compilers, build tools)
FROM python:3.11-slim as builder
RUN apt-get install build-essential
RUN pip install dependencies

# Stage 2: Runtime (only what's needed to run)
FROM python:3.11-slim
COPY --from=builder /root/.local /home/appuser/.local  # Copy only packages!
```

**Benefits:**
- Smaller images (no build tools in production)
- Faster deployments
- Reduced attack surface

### 4. Layer Caching

Change your code and rebuild - notice how fast it is!

```bash
# First build: ~2 minutes (downloads everything)
docker build -t jsonify .

# Change src/cli.py and rebuild: ~2 seconds!
docker build -t jsonify .
```

**Why?** Docker caches layers. Only changed layers are rebuilt.

## Debugging

### Explore Container Filesystem

```bash
# List files in /app
docker run --rm --entrypoint ls jsonify -la /app

# Check Python version
docker run --rm --entrypoint python jsonify --version

# List installed packages
docker run --rm --entrypoint pip jsonify list
```

### Inspect Image

```bash
# See image size
docker images jsonify

# View layer history
docker history jsonify

# Inspect configuration
docker inspect jsonify

# Check entry point and CMD
docker inspect jsonify --format='{{.Config.Entrypoint}} {{.Config.Cmd}}'

# Check user
docker inspect jsonify --format='{{.Config.User}}'
```

### Interactive Shell (for deep debugging)

```bash
# Enter container with bash
docker run -it --rm --entrypoint /bin/bash jsonify

# Now you're inside! Try:
appuser@container:/app$ ls -la
appuser@container:/app$ python -m src.cli --help
appuser@container:/app$ pip list
appuser@container:/app$ exit
```

## Project Structure

```
pythonDocker/
├── Dockerfile              # Multi-stage build with best practices
├── .dockerignore           # Excludes junk from image
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── __main__.py        # Makes module executable
│   ├── cli.py             # Click CLI (Command pattern)
│   ├── json_processor.py  # JSON operations
│   ├── csv_processor.py   # CSV operations
│   └── utils.py           # Shared utilities
└── examples/
    ├── sample.json        # Test data
    ├── users.csv
    └── users.json
```

## Docker Best Practices Applied

✅ **Multi-stage builds** - Separate build and runtime stages
✅ **Layer caching** - Dependencies before code (faster rebuilds)
✅ **Non-root user** - Runs as `appuser` for security
✅ **.dockerignore** - Excludes unnecessary files
✅ **Minimal base image** - `python:3.11-slim` (not full)
✅ **No cache** - `pip install --no-cache-dir` (smaller image)
✅ **Cleanup** - `rm -rf /var/lib/apt/lists/*` after apt-get
✅ **Python optimizations** - `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`
✅ **Entrypoint + CMD** - Flexible command structure
✅ **Metadata labels** - Maintainer, description, version

## Common Docker Commands Cheat Sheet

```bash
# Build
docker build -t jsonify .                    # Build image
docker build -t jsonify:v2 .                 # Build with tag
docker build --no-cache -t jsonify .         # Force rebuild (no cache)

# Run
docker run --rm jsonify                      # Run and auto-remove
docker run -i --rm jsonify                   # With stdin
docker run -it --rm jsonify                  # Interactive + TTY
docker run -d jsonify                        # Detached (background)

# Volumes
docker run -v $(pwd):/data jsonify           # Mount current directory
docker run -v $(pwd):/data:ro jsonify        # Read-only mount
docker run -v my-volume:/data jsonify        # Named volume

# Inspect
docker images                                # List all images
docker ps                                    # List running containers
docker ps -a                                 # List all containers
docker inspect jsonify                       # Image details
docker history jsonify                       # Layer history
docker logs <container-id>                   # View logs

# Clean up
docker rm <container-id>                     # Remove container
docker rmi jsonify                           # Remove image
docker system prune                          # Remove unused data
docker system prune -a                       # Remove all unused images
```

## What You Learned

By building this project, you now understand:

1. **Docker fundamentals**
   - Difference between images and containers
   - How layers work and why they matter
   - Layer caching for faster builds

2. **Dockerfile best practices**
   - Multi-stage builds for smaller images
   - Ordering commands for optimal caching
   - Security: non-root users, minimal images
   - Cleanup: removing caches and temp files

3. **Practical Docker usage**
   - Volume mounting for file processing
   - stdin/stdout for pipeline integration
   - Read-only volumes for safety
   - Debugging containers

4. **Python CLI patterns**
   - Click framework (Command pattern)
   - Module structure
   - stdin/stdout handling
   - Error handling

## Next Steps

To continue learning Docker:

1. **Add a database**: Create a PostgreSQL container and connect to it
2. **Docker Compose**: Define multi-container applications
3. **Environment variables**: Configure the app via ENV vars
4. **Health checks**: Add HEALTHCHECK to Dockerfile
5. **CI/CD**: Auto-build images on git push
6. **Docker Hub**: Publish your image to share with others

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Python Docker Images](https://hub.docker.com/_/python)

