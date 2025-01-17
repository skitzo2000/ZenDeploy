.PHONY: clean test setup help

# Default target
help:
	@echo "ZenDeploy Make Commands"
	@echo "----------------------"
	@echo "make setup    - Set up test environment"
	@echo "make test     - Run tests"
	@echo "make clean    - Clean up test environment and cache files"
	@echo "make all      - Clean, setup, and test"

# Setup test environment
setup:
	@echo "Setting up test environment..."
	python3 tests/setup_test_env.py

# Run tests
test: setup
	@echo "Running tests..."
	python3 -m pytest tests/

# Clean up
clean:
	@echo "Cleaning up test environment..."
	rm -rf tests/test_repos/
	rm -rf logs/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.log" -delete

# All in one command
all: clean setup test 