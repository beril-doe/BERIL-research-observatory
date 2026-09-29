# Use the UV-preinstalled python image
FROM ghcr.io/astral-sh/uv:0.12.20-python3.12-trixie-slim

# Add SPIN user id. `--home` + `--shell` give the account a real, writable
# HOME — without these, `adduser --system` defaults to HOME=/nonexistent,
# which breaks any tool that reads/writes under $HOME (e.g. the bundled
# `claude` CLI used by the chat feature hangs on its config path).
RUN addgroup --system --gid 76761 beril_app
RUN adduser --system --uid 76761 \
    --home /home/beril \
    --shell /bin/bash \
    --ingroup beril_app \
    beril

# Create public directory with proper permissions for beril user to write config
RUN mkdir -p /tmp/beril_data_cache && \
    chown beril:beril_app /tmp/beril_data_cache && \
    chmod 755 /tmp/beril_data_cache

# Set working directory to the repository root
WORKDIR /repo

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Omit development dependencies
ENV UV_NO_DEV=1

# Install git
RUN apt-get update && \
    apt-get install -y git

# Copy only the dependency manifests first. Installing dependencies separately
# from the source that depends on them keeps this layer cached across ordinary
# code edits — without the split, touching any file under ui/app reinstalls all
# ~89 packages.
COPY ui/pyproject.toml ui/pyproject.toml
COPY ui/uv.lock ui/uv.lock

# Install dependencies (not the project itself — its source isn't copied yet).
# `--locked` fails the build if uv.lock has drifted from pyproject.toml, turning
# a forgotten `uv lock` into a red build instead of an image that silently
# misses a dependency.
RUN uv sync --locked --no-install-project --directory ui/

# Then the application source, and install the project itself against the
# already-resolved dependency layer above.
COPY ui/app ui/app
COPY ui/alembic ui/alembic
COPY ui/alembic.ini ui/alembic.ini
RUN uv sync --locked --directory ui/

# Copy all necessary repository directories
COPY projects ./projects
COPY docs ./docs
COPY data ./data
COPY atlas ./atlas
COPY ui/config ./ui/config

# Expose port 8000
EXPOSE 8000

# Set working directory to UI for running the app
WORKDIR /repo/ui

# Put the uv-managed venv at the front of PATH. `uv sync` installs into
# /repo/ui/.venv rather than the system Python the way `uv pip install --system`
# used to, so without this the CMD below fails at runtime with
# "sh: 1: alembic: not found" even though the image builds cleanly.
ENV PATH="/repo/ui/.venv/bin:$PATH"

USER beril

ARG GIT_COMMIT
ARG BUILD_DATE
ENV BERIL_GIT_COMMIT=${GIT_COMMIT}
ENV BERIL_BUILD_DATE=${BUILD_DATE}

# Run the application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=\"*\""]
