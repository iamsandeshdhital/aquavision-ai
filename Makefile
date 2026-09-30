.PHONY: help install test lint run docker-build docker-run clean

PYTHON := python3
PIP := pip3

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov flake8

test:
	$(PYTHON) -m pytest tests/ -v --cov=core --cov-report=term-missing

lint:
	flake8 core tests --count --select=E9,F63,F7,F82 --show-source --statistics

run:
	$(PYTHON) aquavision.py --config config.yaml

run-demo:
	$(PYTHON) aquavision.py --config config.yaml --demo

docker-build:
	docker build -t aquavision-ai:latest .

docker-run:
	docker run -p 8050:8050 -v $(PWD)/data:/app/data aquavision-ai:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf core/__pycache__ tests/__pycache__
	rm -rf data/*.db
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

setup:
	mkdir -p data
	touch data/.gitkeep
