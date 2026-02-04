.PHONY: help server web install clean

# Default target: display help
help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  server   Start the Backend API server (Flask)"
	@echo "  web      Open the Hotel Assistant web widget in your browser"
	@echo "  logs     Watch server logs in real-time"
	@echo "  install  Install Python dependencies"
	@echo "  clean    Remove temporary files and caches"

# Start the Flask backend server (without auto-reload for stability)
server:
	@echo "Starting Hotel Assistant Server..."
	@FLASK_DEBUG=0 /Users/andreyzherditskiy/work/zai-voice-2/.venv/bin/python api/index.py

# Start server in background
server-bg:
	@echo "Starting Hotel Assistant Server in background..."
	@FLASK_DEBUG=0 /Users/andreyzherditskiy/work/zai-voice-2/.venv/bin/python api/index.py > server_run.log 2>&1 &
	@sleep 2
	@curl -s http://127.0.0.1:8000/api/health > /dev/null && echo "✓ Server running on http://localhost:8000" || echo "✗ Server failed to start"

# Open the web widget in the default browser
web:
	@echo "Opening Hotel Assistant..."
	@open "http://localhost:8000/hotel.html"

# Watch logs
logs:
	@echo "Tailing server logs..."
	@tail -f server.log

# Install dependencies
install:
	@echo "Installing dependencies..."
	@/Users/andreyzherditskiy/work/zai-voice-2/.venv/bin/python -m pip install -r api/requirements.txt

# Clean up
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
