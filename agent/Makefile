.PHONY: install format lint test clean dev-setup

# Install dependencies
install:
	pip install -r requirements.txt

# Development setup
dev-setup: install
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Auto import sorting and formatting will now run on git commits."

# Format code
format:
	isort . --profile black --line-length 88
	black . --line-length 88

# Lint code
lint:
	flake8 . --max-line-length 88 --extend-ignore E203,W503
	mypy . --ignore-missing-imports
	isort . --profile black --line-length 88 --check-only

# Run tests
test:
	pytest

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete

# Run the application
run:
	python main.py

# Run with Docker
docker-run:
	docker-compose up --build

# Sort imports manually
sort-imports:
	isort . --profile black --line-length 88
