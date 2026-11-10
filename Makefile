.PHONY: help dev tailwind test migrate check shell clean

PYTHON ?= python3

help:
	@echo "DHAT Stack (Django + HTMX + Alpine.js + Tailwind v4) Boilerplate"
	@echo "Available commands:"
	@echo "  make dev        - Run Django development server"
	@echo "  make tailwind   - Run Tailwind CSS CLI in watch mode"
	@echo "  make test       - Run automated test suite (test.py)"
	@echo "  make check      - Run Django system configuration checks"
	@echo "  make migrate    - Apply database migrations"
	@echo "  make shell      - Open Django interactive shell"
	@echo "  make clean      - Clean up __pycache__ and build artifacts"

dev:
	$(PYTHON) manage.py runserver

tailwind:
	$(PYTHON) manage.py tailwind watch

test:
	$(PYTHON) test.py

check:
	$(PYTHON) manage.py check

migrate:
	$(PYTHON) manage.py migrate

shell:
	$(PYTHON) manage.py shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
