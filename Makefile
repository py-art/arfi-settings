.DEFAULT_GOAL := help
sources = arfi_settings tests

.PHONY: .pdm  ## Check that PDM is installed
.pdm:
	@pdm -V || echo 'Please install PDM: https://pdm.fming.dev/latest/#installation'

.PHONY: .pre-commit  ## Check that pre-commit is installed
.pre-commit:
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: install  ## Install the package, dependencies, and pre-commit for local development
install: .pdm .pre-commit
	python3 -m venv .venv
	pdm info
	pdm venv create --with-pip --force 3.11
	pdm install --group :all
	pdm run pre-commit install --install-hooks

.PHONY: refresh-lockfiles  ## Sync lockfiles with requirements files.
refresh-lockfiles: .pdm
	pdm update --update-reuse --group :all

.PHONY: rebuild-lockfiles  ## Rebuild lockfiles from scratch, updating all dependencies
rebuild-lockfiles: .pdm
	pdm update --update-eager --group :all

.PHONY: format  ## Auto-format python source files
format: .pdm
	pdm run ruff check --fix $(sources)
	pdm run ruff format $(sources)

.PHONY: lint  ## Lint python source files
lint: .pdm
	pdm run ruff check $(sources)
	pdm run ruff format --check $(sources)

.PHONY: sync  ## Sync and remove extra dependencies
sync: .pdm rebuild-lockfiles
	pdm sync --clean

.PHONY: clean  ## Clear local caches and build artifacts
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -rf site
	rm -rf docs/_build
	rm -rf docs/.changelog.md docs/.version.md docs/.tmp_schema_mappings.html
	rm -rf coverage.xml
	rm -rf .mypy_cache

.PHONY: test  ## Run all tests, skipping the type-checker integration tests
test: .pdm
	pdm run coverage run -m pytest --durations=10

.PHONY: testcov  ## Run tests and generate a coverage report, skipping the type-checker integration tests
testcov: test
	@echo "building coverage html"
	@pdm run coverage html

.PHONY: testopen  ## Open a coverage report
testopen: testcov
	@xdg-open ./htmlcov/index.html

t:
	clear && pytest

tc:
	clear && pytest -vs -m current

tvc:
	clear && pytest -vvs -m current

.PHONY: docs  ## Run docs http://127.0.0.1:8008
docs: .pdm
	pdm run mkdocs serve -a 127.0.0.1:8008

.PHONY: build-library ## Build library
build-library: .pdm
	pdm build

.PHONY: publish-library ## Publish library (no build)
publish-library: .pdm
	pdm publish --no-build

.PHONY: help  ## Display this message
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
