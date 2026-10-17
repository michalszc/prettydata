.PHONY: help install install-dev test test-verbose lint lint-fix format format-check type-check build check-build publish-test publish validate-version release-metadata release-select-commit release notebooks-check docs docs-serve clean
.DEFAULT_GOAL := help

PYTHON ?= python
TEST_PATH ?= tests/
PYTEST_ARGS ?=
VALIDATE_VERSION_ARGS ?=

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
	$(PYTHON) -m ruff check src/ tests/ scripts/

lint-fix: ## Run linting with auto-fix
	$(PYTHON) -m ruff check --fix src/ tests/ scripts/

format: ## Format code (ruff format)
	$(PYTHON) -m ruff format src/ tests/ scripts/

format-check: ## Check code formatting without making changes
	$(PYTHON) -m ruff format --diff src/ tests/ scripts/

type-check: ## Run type checking (mypy)
	$(PYTHON) -m mypy src/prettydata/ tests/ scripts/

build: ## Build package for distribution
	$(PYTHON) -m build

publish-test: ## Publish to TestPyPI
	$(PYTHON) -m twine upload --repository testpypi dist/*

publish: ## Publish to PyPI
	$(PYTHON) -m twine upload dist/*

check-build: ## Check if build is ready for publishing
	$(PYTHON) -m twine check dist/*

release-metadata: ## Record the current commit and package version without publishing
	$(PYTHON) scripts/release.py metadata --output "$(or $(RELEASE_METADATA),release-metadata.json)"

release-select-commit: ## Select the deployed commit from validated CD metadata
	$(PYTHON) scripts/release.py select-commit --metadata "$(or $(RELEASE_METADATA),release-metadata.json)"

release: ## Publish a GitHub release for the checkout recorded in deployment metadata
	$(PYTHON) scripts/release.py publish --metadata "$(or $(RELEASE_METADATA),release-metadata.json)" --project "$(or $(RELEASE_PROJECT),.)" --repository "$(or $(RELEASE_REPOSITORY),$(GITHUB_REPOSITORY))"

validate-version: ## Check project versions, release notes, and PyPI
	@PYTHON="$(PYTHON)" bash scripts/validate_version.sh $(VALIDATE_VERSION_ARGS)

notebooks-check: ## Validate saved notebooks without executing cells
	@PYTHON="$(PYTHON)" bash scripts/validate_notebooks.sh

docs: ## Validate and generate documentation using strict MkDocs checks
	NO_MKDOCS_2_WARNING=1 $(PYTHON) -m mkdocs build --strict
	@echo "📚 Documentation generated in docs/ directory"

docs-serve: ## Serve documentation locally using MkDocs
	@echo "🌐 Starting local server at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	NO_MKDOCS_2_WARNING=1 $(PYTHON) -m mkdocs serve --dev-addr 127.0.0.1:8000

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
	find src tests scripts -type d -name __pycache__ -exec rm -rf {} +
	find src tests scripts -name '*.py[co]' -delete
