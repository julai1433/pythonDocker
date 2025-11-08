# ═══════════════════════════════════════════════════════════
# Stage 1: Builder
# Purpose: Install dependencies and prepare the application
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building Python packages
# Note: Some Python packages require C compilers to build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
# If requirements.txt doesn't change, Docker reuses this layer
COPY requirements.txt .

# Install Python dependencies to user directory
# --user: Installs to ~/.local (easier to copy to next stage)
# --no-cache-dir: Don't save pip's download cache (saves ~100MB)
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Optional: Run tests during build (uncomment when you have tests)
# RUN python -m pytest tests/

# ═══════════════════════════════════════════════════════════
# Stage 2: Runtime
# Purpose: Minimal production image with only what's needed to run
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim

# Create non-root user for security
# -m: Create home directory
# -u 1000: Set UID to 1000 (matches most host users for easier file permissions)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage to appuser's home
# This is the magic of multi-stage builds - we get the packages without the build tools!
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy only application source code (not tests, docs, etc.)
# --chown: Set ownership to appuser (not root)
COPY --chown=appuser:appuser src/ ./src/

# Make sure scripts in .local are in PATH for appuser
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/home/appuser/.local/lib/python3.11/site-packages

# Python optimizations for Docker
# PYTHONUNBUFFERED=1: Don't buffer stdout/stderr (see logs immediately)
# PYTHONDONTWRITEBYTECODE=1: Don't create .pyc files (cleaner container)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user for security
# Everything from here runs as 'appuser', not root
USER appuser

# Set entrypoint (always runs) and default command (can be overridden)
# User runs: docker run jsonify prettify
# Executes: python -m src.cli prettify
ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["--help"]

# Metadata labels (good practice for production images)
LABEL maintainer="julio@example.com" \
      description="JSON/CSV transformer CLI tool for learning Docker" \
      version="1.0.0"
