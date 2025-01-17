# ZenDeploy Configuration Guide

## Theme Configuration

The application's appearance and behavior can be customized through the `theme.yml` file:

```yaml
app_name: "ZENDEPLOY"
display_version: "0.1"
author: "Your Name"
date: "2024"
description: "Your description"

splash:
  prompt: "Press any key to continue..."
  font: "big"  # See font options below
  box:
    enabled: true
    style: "double"  # single, double, or heavy
  colors:
    title: "bright_blue"
    subtitle: "white"
    version: "grey70"
    prompt: "yellow"
```

### Available Fonts
- `banner3` - Good for wide displays
- `speed` - Tech looking, compact
- `big` - Classic, readable
- `doom` - Gaming style
- `isometric1` - 3D effect
- `larry3d` - 3D with shadows
- `digital` - LCD display style
- `slant` - Default

## Deployment Configuration

Each deployment step is defined in a YAML file with the following structure:

```yaml
name: "Deployment Step Name"
aws_profile: "profile-name"
repo_url: "git@github.com:user/repo.git"
ssh_key: "/path/to/ssh/key"
script_path: "deploy/script.sh"
env_vars:
  ENV_VAR1: "value1"
  ENV_VAR2: "value2"
```

### Required Fields
- `name`: Descriptive name for the deployment step
- `aws_profile`: AWS CLI profile to use
- `repo_url`: Git repository URL (SSH or HTTPS)
- `ssh_key`: Path to SSH key for repository access
- `script_path`: Path to deployment script within repository

### Optional Fields
- `env_vars`: Dictionary of environment variables

## Testing Configuration

To test your configuration:

1. Create a test deployment YAML:
```yaml
name: "Test Deployment"
aws_profile: "test-profile"
repo_url: "file://tests/test_repos/repo1"
ssh_key: "~/.ssh/id_rsa"
script_path: "scripts/hello.sh"
env_vars:
  TEST_VAR: "test_value"
```

2. Run the test environment setup:
```bash
python3 tests/setup_test_env.py
```

3. Start ZenDeploy and try loading your test configuration:
```bash
python3 src/main.py
```

## Validation

ZenDeploy validates configurations before execution:
- Checks for required fields
- Validates AWS profile existence
- Verifies Git repository access
- Confirms script path exists

## Common Issues

- SSH key permissions should be 600 (`chmod 600 ~/.ssh/id_rsa`)
- Script files must be executable (`chmod +x script.sh`)
- AWS profiles must be configured in `~/.aws/config`
