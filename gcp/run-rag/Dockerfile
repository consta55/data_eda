# Use an official lightweight Python image as the base
FROM python:3.11-slim

# Set environment variables for Python and pip behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup"  \
    VENV_PATH="/opt/pysetup/.venv"

# Update PATH to include Poetry and the virtual environment binaries
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Update package list and install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential

# Install Poetry (Python dependency management tool)
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python

# Set the working directory for Python setup
WORKDIR $PYSETUP_PATH

# Copy Poetry's dependency files into the container
COPY poetry.lock pyproject.toml ./

# Install Python dependencies inside the virtual environment
RUN poetry install --no-dev

# Copy the rest of the application code into the container
COPY . .

# Expose port 8080 to the host
EXPOSE 8080

# Command to start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]