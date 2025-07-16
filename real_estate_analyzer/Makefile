.PHONY: help install run-dev run-prod test clean docker-build

help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies" 
	@echo "  run-dev          - Start development server"
	@echo "  run-prod         - Start production server (env vars: HOST, PORT)"
	@echo "  run-prod-config  - Start production server using gunicorn.conf.py"
	@echo "  run-prod-local   - Start production server locally (127.0.0.1:8051)"
	@echo "  test             - Run tests"
	@echo "  clean            - Clean build artifacts"
	@echo "  docker-build     - Build Docker image"

install:
	pip install -r requirements.txt

run-dev:
	python cli.py serve --debug

run-prod:
	gunicorn --bind $${HOST:-0.0.0.0}:$${PORT:-8000} --workers 4 wsgi:application

run-prod-config:
	gunicorn -c gunicorn.conf.py wsgi:application

run-prod-local:
	gunicorn --bind 127.0.0.1:8051 --workers 2 wsgi:application

test:
	python -m pytest tests/

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info/

docker-build:
	docker build -t real-estate-analyzer . 