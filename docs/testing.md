# ZenDeploy Testing Guide

## Quick Start

ZenDeploy uses Make commands to simplify testing:

```bash
# Clean everything and run tests
make all

# Individual commands
make clean    # Clean up test environment
make setup    # Set up test environment
make test     # Run tests
```

## Setting Up the Test Environment

The test environment can be set up in two ways:

1. Using Make (recommended):
```bash
make setup
```

2. Manually:
=======
## Setting Up the Test Environment

Before running tests, you need to set up the test environment which creates local repositories and test files.

1. Run the test environment setup script:


```bash
python3 tests/setup_test_env.py
```

## Cleaning Up

Before submitting code or if you encounter issues, clean the test environment:

```bash
make clean
```

This will remove:
- Test repositories
- Python cache files
- Log files
- Test cache
- Compiled Python files
=======
2. Verify the test environment:
   - Check that the `tests/test_repos` directory was created
   - Verify that test repositories contain the required scripts

## Test Structure

The test environment creates:
- Local Git repositories for testing deployment scripts
- Sample YAML configuration files
- Test deployment scripts

## Running Tests
Tests are run thru the TUI interface.  Navigate to the test folder with the test deployment yamls add as you like as the test.