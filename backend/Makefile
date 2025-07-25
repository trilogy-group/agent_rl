.PHONY: dev run install clean

# Install dependencies
install:
	poetry install

# Run server in development mode with auto-reload
dev:
	poetry run uvicorn src.langgraph_server:app --host 0.0.0.0 --port 8000 --reload

# Run server normally
run:
	poetry run python src/langgraph_server.py

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Help
help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Run server in development mode with auto-reload"
	@echo "  run      - Run server normally"
	@echo "  clean    - Clean cache files"