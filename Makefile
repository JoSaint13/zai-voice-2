.PHONY: help venv install run run-bg stop reload web logs test clean

PY ?= python3
VENV ?= .venv
BIN  ?= $(VENV)/bin
PYTHON ?= $(BIN)/python
PIP ?= $(BIN)/pip
HOST ?= 0.0.0.0
PORT ?= 8088

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  venv        Create local virtualenv (.venv)"
	@echo "  install     Install deps into .venv (requirements.txt)"
	@echo "  run         Start Flask API (loads .env, Chutes voice ready)"
	@echo "  run-bg      Start API in background -> server_run.log"
	@echo "  stop        Stop API on port $(PORT)"
	@echo "  web         Open http://localhost:$(PORT)"
	@echo "  logs        Tail server_run.log"
	@echo "  test        Run pytest -q"
	@echo "  clean       Remove __pycache__ and *.pyc"

$(BIN)/python:
	@$(PY) -m venv $(VENV)
	@$(PYTHON) -m pip install -U pip

venv: $(BIN)/python

install: venv
	@$(PYTHON) -m pip install -r requirements.txt

run: venv
	@echo "Starting API on $(HOST):$(PORT)..."
	@FLASK_DEBUG=0 HOST=$(HOST) PORT=$(PORT) $(PYTHON) api/index.py

run-bg: venv
	@echo "Starting API in background on $(HOST):$(PORT)..."
	@FLASK_DEBUG=0 HOST=$(HOST) PORT=$(PORT) $(PYTHON) api/index.py > server_run.log 2>&1 &
	@sleep 2
	@curl -s http://127.0.0.1:$(PORT)/api/health > /dev/null && echo "✓ http://localhost:$(PORT)" || echo "✗ server failed"

stop:
	@echo "Stopping server on port $(PORT)..."
	@PID=$$(lsof -ti:$(PORT)); \
	if [ -n "$$PID" ]; then kill $$PID 2>/dev/null && echo "✓ Stopped PID $$PID"; else echo "No server on $(PORT)"; fi

reload: stop
	@$(MAKE) run

web:
	@echo "Opening web UI..."
	@open "http://localhost:$(PORT)"

logs:
	@echo "Tailing server_run.log..."
	@tail -f server_run.log

test: venv
	@$(PYTHON) -m pytest -q

clean:
	@echo "Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
