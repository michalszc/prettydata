.PHONY: help install install-dev test test-verbose lint lint-fix format format-check type-check clean
.DEFAULT_GOAL := help

PYTHON ?= python
TEST_PATH ?= tests/
PYTEST_ARGS ?=

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	$(PYTHON) -m pip install -e .

install-dev: ## Install package with development dependencies
	$(PYTHON) -m pip install -e '.[all]' --group dev
	$(PYTHON) -m pre_commit install

test: ## Run tests
	$(PYTHON) -m pytest $(TEST_PATH) $(PYTEST_ARGS) --cov=src/prettydata --cov-report=term-missing --cov-report=html

test-verbose: ## Run tests with verbose output
	$(PYTHON) -m pytest $(TEST_PATH) $(PYTEST_ARGS) -v --cov=src/prettydata --cov-report=term-missing

lint: ## Run linting (ruff check)
	$(PYTHON) -m ruff check src/ tests/

lint-fix: ## Run linting with auto-fix
	$(PYTHON) -m ruff check --fix src/ tests/

format: ## Format code (ruff format)
	$(PYTHON) -m ruff format src/ tests/

format-check: ## Check code formatting without making changes
	$(PYTHON) -m ruff format --diff src/ tests/

type-check: ## Run type checking (mypy)
	$(PYTHON) -m mypy src/prettydata/ tests/

clean: ## Clean artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf docs/
	find src tests -type d -name __pycache__ -exec rm -rf {} +
	find src tests -name '*.py[co]' -delete
