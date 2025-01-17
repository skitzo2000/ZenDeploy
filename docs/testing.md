# ZenDeploy Testing Guide

## Setting Up the Test Environment

Before running tests, you need to set up the test environment which creates local repositories and test files.

1. Run the test environment setup script:
```bash
python3 tests/setup_test_env.py
```

2. Verify the test environment:
   - Check that the `tests/test_repos` directory was created
   - Verify that test repositories contain the required scripts

## Running Tests

[Test documentation to be added]

## Test Structure

The test environment creates:
- Local Git repositories for testing deployment scripts
- Sample YAML configuration files
- Test deployment scripts

## Writing New Tests

[Test writing documentation to be added] 