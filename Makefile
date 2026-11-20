PYTHON ?= python3
VENV ?= venv
VENV_PYTHON := $(VENV)/bin/python
CLAUDE ?= claude
SCORECARD ?= scorecard
NODE ?= node
NPM ?= npm
PLAYWRIGHT_INSTALL_ARGS ?=
PY_DIRS := scripts skills tests tools

.DEFAULT_GOAL := help

.PHONY: help setup dev-deps browser-deps setup-board-browser lint format test test-live test-scorecard check plugin-validate check-board-browser clean

help: ## Show available targets.
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: $(VENV_PYTHON) ## Create the local Python virtual environment.

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

dev-deps: $(VENV)/.maintenance-deps ## Install the pinned development-only dependencies.

$(VENV)/.maintenance-deps: requirements-dev.txt $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install --quiet -r requirements-dev.txt
	@touch "$@"

lint: dev-deps ## Check formatting and lint rules without changing files.
	$(VENV_PYTHON) -m ruff format --check $(PY_DIRS)
	$(VENV_PYTHON) -m ruff check $(PY_DIRS)

format: dev-deps ## Apply the formatter and the lint rules' safe fixes.
	$(VENV_PYTHON) -m ruff format $(PY_DIRS)
	$(VENV_PYTHON) -m ruff check --fix $(PY_DIRS)

test: dev-deps ## Run offline tests, combine subprocess coverage, and enforce both floors.
	$(VENV_PYTHON) -m coverage erase
	@# Tests create temporary repositories; do not inherit the invoking hook's Git context.
	@git_env_vars=$$(git rev-parse --local-env-vars) && unset $$git_env_vars || exit 1; \
	$(VENV_PYTHON) -W error::ResourceWarning -m coverage run -m unittest discover -s tests -t tests
	$(VENV_PYTHON) -m coverage combine
	$(VENV_PYTHON) -m coverage report
	$(VENV_PYTHON) -m coverage json -o coverage/coverage.json
	$(VENV_PYTHON) tools/check_coverage.py coverage/coverage.json

test-live: setup ## Check the plugin against the pinned MCP server (starts it with uvx; needs network).
	$(VENV_PYTHON) -m unittest discover -s tests/live -t tests/live -v

test-scorecard: setup ## Check the installed Scorecard build against controlled MCP responses and local CLI fixtures.
	SCORECARD="$(SCORECARD)" $(VENV_PYTHON) -W error::ResourceWarning -m unittest discover -s tests/scorecard_live -t tests/scorecard_live -v

check: lint test ## Run lint, tests with coverage, and compile every Python source file.
	$(VENV_PYTHON) -m compileall -q $(PY_DIRS)

plugin-validate: ## Validate the plugin's structure when Claude Code is installed.
	$(CLAUDE) plugin validate --strict .

browser-deps: .github/ci/node_modules/.package-lock.json ## Install pinned CI-only JavaScript dependencies.

.github/ci/node_modules/.package-lock.json: .github/ci/package.json .github/ci/package-lock.json
	$(NPM) ci --prefix .github/ci --ignore-scripts --no-audit --no-fund

setup-board-browser: browser-deps ## Install the test Chromium browser (needs network once).
	$(NODE) .github/ci/node_modules/playwright/cli.js install $(PLAYWRIGHT_INSTALL_ARGS) chromium

check-board-browser: setup browser-deps ## Run headless board regressions with a disposable offline fixture.
	$(NODE) .github/ci/run-board-browser.cjs "$(VENV_PYTHON)"

clean: ## Remove generated local test and Python cache files.
	find $(PY_DIRS) -type d -name __pycache__ -prune -exec rm -r {} + 2>/dev/null || true
	find $(PY_DIRS) -type f -name '*.pyc' -delete 2>/dev/null || true
