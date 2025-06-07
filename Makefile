.PHONY: help install install-jupyter install-dev setup clean lint format test pre-commit-setup
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-jupyter: ## Install with Jupyter dependencies
	pip install -e ".[jupyter]"

install-dev: ## Install development dependencies
	pip install -e ".[dev,jupyter]"

setup: install-jupyter ## Basic setup (Jupyter only)
	@echo "✅ Basic setup complete!"
	@echo "Jupyter and basic dependencies installed"

dev-setup: install-dev pre-commit-setup ## Complete development setup
	@echo "✅ Development environment setup complete!"
	@echo "Run 'make lint' to check code quality"
	@echo "Run 'make test' to run tests"

clean: ## Clean cache files and build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Development commands (require dev dependencies)
lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	ruff check src/
	black --check src/
	mypy src/

format: ## Format code with black and ruff
	@echo "🎨 Formatting code..."
	black src/
	ruff check --fix src/

test: ## Run tests (when tests directory exists)
	@echo "🧪 Running tests..."
	pytest tests/ -v

pre-commit-setup: ## Install pre-commit hooks
	@echo "🔧 Installing pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg

pre-commit-run: ## Run pre-commit on all files
	@echo "🚀 Running pre-commit on all files..."
	pre-commit run --all-files
