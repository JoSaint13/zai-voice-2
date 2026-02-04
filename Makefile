.PHONY: help server web install clean

# Default target: display help
help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  server   Start the Backend API server (Flask)"
	@echo "  web      Open the Hotel Assistant web widget in your browser"
	@echo "  install  Install Python dependencies"
	@echo "  clean    Remove temporary files and caches"

# Start the Flask backend server
server:
	@echo "Starting Hotel Assistant Server..."
	@/Users/andreyzherditskiy/work/zai-voice-2/.venv/bin/python api/index.py

# Open the web widget in the default browser
web:
	@echo "Opening Hotel Assistant..."
	@open "http://localhost:8000/hotel.html"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@/Users/andreyzherditskiy/work/zai-voice-2/.venv/bin/python -m pip install -r api/requirements.txt

# Clean up
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
