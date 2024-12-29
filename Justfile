# Justfile for FastAPI Project

# Install project dependencies using Poetry
install:
    python -m build .

# Run tests using Poetry and pytest
test:
    pytest

# Format code using Poetry and black
format:
    ruff format src/

check:
    ruff check src/

# Clean up generated files
clean:
    rm -rf **/__pycache__ .pytest_cache

# Run the development environment (install, run, and watch for changes)
dev:
    just install
    just run