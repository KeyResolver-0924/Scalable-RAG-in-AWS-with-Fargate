# Makefile

.PHONY: req lint clean

# Variables
PIP := pip
RUFF := ruff
PYTHONPATH := $(shell pwd)/src

all: req lint test clean ## Run all tasks

req: ## Install the requirements
	$(PIP) install -r requirements.txt

lint: ## Run linter and code formatter (ruff)
	$(RUFF) check . --fix  

test: ## Run tests using pytest
	PYTHONPATH=$(PYTHONPATH) pytest tests/

clean: ## Clean up generated files
	rm -rf __pycache__
