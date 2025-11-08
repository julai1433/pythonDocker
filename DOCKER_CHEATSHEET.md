# Docker Quick Reference - For This Project

## Essential Commands You'll Use Daily

### Building

```bash
# Build image (first time or after Dockerfile changes)
docker build -t jsonify .

# Rebuild without cache (when things get weird)
docker build --no-cache -t jsonify .

# Build with a specific tag
docker build -t jsonify:v1.0 .
```

### Running

```bash
# Basic run (shows help)
docker run --rm jsonify

# With stdin (for piping data in)
docker run -i --rm jsonify prettify

# With file mounting
docker run --rm -v $(pwd)/examples:/data jsonify prettify -i /data/file.json

# Read-only mount (prevents modifications)
docker run --rm -v $(pwd)/examples:/data:ro jsonify validate -i /data/file.json
```

**Key flags:**
- `--rm` - Auto-remove container after it exits (cleanup)
- `-i` - Keep stdin open (required for piping data)
- `-v` - Mount volume (share files with container)
- `:ro` - Make volume read-only

### Inspecting

```bash
# List images
docker images

# See image details
docker inspect jsonify

# View layer history (see what each layer adds)
docker history jsonify

# Check what user container runs as
docker inspect jsonify --format='{{.Config.User}}'
```

### Debugging

```bash
# Override entrypoint to explore container
docker run --rm --entrypoint ls jsonify -la /app
docker run --rm --entrypoint python jsonify --version
docker run --rm --entrypoint pip jsonify list

# Enter container interactively
docker run -it --rm --entrypoint /bin/bash jsonify
# Now you're inside! Type 'exit' to leave
```

### Cleaning Up

```bash
# Remove specific image
docker rmi jsonify

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused (nuclear option)
docker system prune -a

# See disk usage
docker system df
```

## Common Patterns

### Pattern 1: Process File, Save Result

```bash
# Read from examples/, write to examples/
docker run --rm -v $(pwd)/examples:/data jsonify \
  prettify -i /data/sample.json -o /data/pretty.json
```

### Pattern 2: Pipeline (Unix-style)

```bash
# Pipe through Docker containers
cat data.json | docker run -i --rm jsonify prettify | \
                docker run -i --rm jsonify minify

# Combine with curl
curl https://api.github.com/repos/docker/docker | \
  docker run -i --rm jsonify prettify
```

### Pattern 3: Batch Processing

```bash
# Process all JSON files in a directory
for file in examples/*.json; do
  docker run --rm -v $(pwd)/examples:/data jsonify \
    prettify -i /data/$(basename $file) -o /data/pretty-$(basename $file)
done
```

## Understanding Flags

### Volume Mounts: `-v`

```bash
-v /absolute/path/on/mac:/path/in/container
   └─────┬─────┘            └────┬────┘
         │                        └─ Where container sees it
         └─ Your Mac's filesystem

# Examples:
-v $(pwd):/data                    # Current directory → /data
-v $(pwd)/examples:/data           # examples/ subdirectory → /data
-v $(pwd)/examples:/data:ro        # Read-only mount
-v my-named-volume:/data           # Named volume (persists)
```

**When to use:**
- Processing files from your Mac
- Saving output back to Mac
- Sharing configuration files

### stdin/Interactive: `-i` and `-it`

```bash
-i       # Keep stdin open (for piping)
-t       # Allocate pseudo-TTY (terminal)
-it      # Both (for interactive shells)

# Examples:
echo '{"a":1}' | docker run -i jsonify prettify     # Pipe in
docker run -it --entrypoint bash jsonify             # Interactive shell
```

### Auto-Remove: `--rm`

```bash
--rm    # Remove container after exit

# Without --rm:
docker run jsonify             # Container remains (uses disk space)
docker ps -a                   # See stopped containers
docker rm <id>                 # Manual cleanup

# With --rm:
docker run --rm jsonify        # Container auto-removed
                               # Cleaner, use this by default!
```

### Override Entrypoint: `--entrypoint`

```bash
--entrypoint <command>   # Replace default entrypoint

# Our default entrypoint: python -m src.cli
# Override to debug:
docker run --entrypoint ls jsonify /app
docker run --entrypoint python jsonify --version
docker run -it --entrypoint bash jsonify    # Get a shell
```

## Dockerfile Concepts

### Layer Caching

```dockerfile
# ❌ BAD - Code changes rebuild everything
COPY . .
RUN pip install -r requirements.txt

# ✅ GOOD - Only rebuilds from changed layer
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**Rule:** Put things that change rarely at the top!

### Multi-Stage Builds

```dockerfile
# Stage 1: Builder (big, has build tools)
FROM python:3.11-slim as builder
RUN apt-get install build-essential
RUN pip install dependencies

# Stage 2: Runtime (small, only runtime)
FROM python:3.11-slim
COPY --from=builder /root/.local /home/appuser/.local
COPY src/ ./src/
```

**Result:** Final image doesn't include build tools!

### .dockerignore

```
# Like .gitignore but for Docker
.git/
__pycache__/
*.pyc
.env
venv/
```

**Why:** Faster builds, smaller images, no secrets in images

## Troubleshooting

### "Image not found"

```bash
# Check if image exists
docker images

# If not, build it
docker build -t jsonify .
```

### "Permission denied" errors

```bash
# Our image runs as 'appuser' (UID 1000)
# If you see permission errors with volumes, check file ownership

# On Mac, this usually isn't an issue
# On Linux, match UIDs: docker run -u $(id -u):$(id -g) ...
```

### "Cannot connect to Docker daemon"

```bash
# Make sure Docker Desktop is running
# Look for whale icon in menu bar
# If not running, open Docker Desktop app
```

### "No space left on device"

```bash
# Docker images pile up! Clean old stuff:
docker system prune -a

# Or be selective:
docker image prune          # Remove dangling images
docker container prune      # Remove stopped containers
```

### Container works, but output is weird

```bash
# If output is buffered, check PYTHONUNBUFFERED
docker inspect jsonify --format='{{.Config.Env}}'
# Should see: PYTHONUNBUFFERED=1

# For debugging, override and check:
docker run --rm -e PYTHONUNBUFFERED=1 jsonify prettify < data.json
```

## Pro Tips

1. **Use `--rm` by default** - Prevents container buildup
2. **Name your volumes** - Easier to manage than anonymous volumes
3. **Tag versions** - `jsonify:v1`, `jsonify:v2`, not just `latest`
4. **Check image size** - `docker images` - keep it reasonable
5. **Layer caching is your friend** - Order Dockerfile wisely
6. **Read logs** - `docker logs <container-id>` for debugging
7. **Use `.dockerignore`** - Faster builds, no accidental secrets

## Real-World Usage

```bash
# Alias for convenience (add to ~/.zshrc or ~/.bashrc)
alias jsonify='docker run -i --rm jsonify'

# Now you can use it like a native command:
echo '{"a":1}' | jsonify prettify
cat file.json | jsonify validate
jsonify --help
```

## Next Steps

Once comfortable with this project:

1. **Try modifying code** - Change `src/cli.py`, rebuild, see caching!
2. **Add a new command** - Implement your own JSON transformation
3. **Optimize image size** - Can you make it smaller than 225MB?
4. **Add tests** - Uncomment test line in Dockerfile
5. **Push to Docker Hub** - Share your image with the world

---

Remember: Docker is just a tool to package and run applications consistently. The concepts you learned here (images, containers, volumes, layers) apply to ANY Docker project!
