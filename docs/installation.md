# ZenDeploy Installation Guide

## Prerequisites

Before installing ZenDeploy, ensure you have the following:

- Python 3.8 or higher
- Git
- AWS CLI configured with profiles
- SSH access to your Git repositories

## Installation Steps

1. Clone the Repository
```bash
git clone <repository_url>
cd zendeploy
```

2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate     # On Windows
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Verifying Installation

To verify your installation:

1. Run the test environment setup:
```bash
python3 tests/setup_test_env.py
```

2. Start the application:
```bash
python3 src/main.py
```

## Troubleshooting

[Troubleshooting documentation to be added]
