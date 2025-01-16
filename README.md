ZenDeploy (ZD)

A Terminal User Interface (TUI) application for managing and executing AWS deployments through YAML configurations. ZenDeploy provides a streamlined way to manage deployment scripts, configure AWS environments, and execute deployments with real-time monitoring and comprehensive audit logging that includes the system user.

The tool allows users to browse deployment YAML files, chain multiple deployment steps together, and execute them while maintaining proper AWS profile management and secure Git repository access. All actions are logged for audit purposes, making it ideal for teams requiring deployment tracking and verification.

There are a few limitations currently:
- This is an alpha stage product it is not ready for production use.
- The application is not fully functional and does not work as expected.
- The application is not fully tested and may not work as expected.
- The application is not fully documented and may not work as expected.
- The application is not fully secure and may not work as expected.

Planned Features/Current fucntional limitations:
- There is no way to clear the deployment list once its created.  You must exit the interface and re enter to clear the list.
- Keybindings show on all pages but not all keys work on all pages, currently there is error handling for mis hit keys. I would like to filter the view to only show keys that are relevant to the current screen.
- Mouse support only works on the main file tree screen and no where else.
- You cannot edit any deployment yamls within the interface.  You must exit and edit with a seperate tool.
- The entire structure is currently in a Development state designed around running the included tests.  Project restructuring will be required to make it production ready.  This is planned for the beta 0.1.0 milestone.
- Plugin Support post 1.0 release milestone:
  - Currently AWS support is embeded but this will be replaced with a plugin system in the future.
  - I would like the system to be modular and allow for plugins to be added for other services such as Azure, GCP, etc. in the future.  As well as supporting other deployment methods such as Docker, Helm, etc. as extra components beyond the standard script deploy.

Project Structure:

zendeploy/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point and TUI initialization
│   ├── deployment_manager.py # Handles deployment step management
│   ├── deployment_executor.py# Executes deployment steps
│   ├── review_screen.py     # Review and execution screen
│   └── audit_logger.py      # Audit logging functionality
├── logs/                    # Directory for audit and deployment logs
├── requirements.txt         # Project dependencies
├── theme.yml               # Application theming configuration
└── README.md              # This file

INSTALLATION AND DEPENDENCIES
---------------------------

Prerequisites:
- Python 3.8+
- Git
- AWS CLI configured with profiles
- SSH access to required Git repositories

Installation Steps:

1. Clone the repository:
   git clone <repository_url>
   cd zendeploy

2. Create a virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   .venv\Scripts\activate     # On Windows

3. Install dependencies:
   pip install -r requirements.txt

Required Dependencies:
- textual: Modern TUI framework for Python
- PyYAML: YAML file parsing and manipulation
- GitPython: Git repository operations
- pyfiglet: ASCII art generation
- rich: Rich text formatting
- typing: Type hints support

USAGE
-----

Starting the Application:
python src/main.py

Configuration:

Theme Configuration (theme.yml):
app_name: "Your App Name"
version: "0.0.1"
author: "Your Name"
date: "2024"
splash:
  title: "ZENDEPLOY"
  subtitle: "Deployment Management System"
  prompt: "Press any key to continue..."
  font: "slant"
  box:
    enabled: true
    style: "double"
  colors:
    title: "bright_blue"
    subtitle: "white"
    version: "grey70"
    prompt: "yellow"

Deployment YAML Structure:
name: "Deployment Step Name"
aws_profile: "profile-name"
repo_url: "git@github.com:user/repo.git"
ssh_key: "/path/to/ssh/key"
script_path: "deploy/script.sh"
env_vars:
  ENV_VAR1: "value1"
  ENV_VAR2: "value2"

KEYBOARD SHORTCUTS
----------------
q: Quit application
Arrow keys: Navigate
Enter: Select/Confirm
Esc: Back/Cancel

LOGGING AND AUDIT
---------------
Audit logs located in logs/ directory
Format: {username}_{timestamp}_audit.log

Audit logs contain:
- User actions
- File operations
- Deployment approvals/denials
- System events

SUPPORT AND CONTRIBUTING
----------------------
For issues and feature requests, please create an issue in the repository's issue tracker.

Want to help? Here's how:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

CREDITS AND REFERENCES
--------------------
This project utilizes the following open source projects:

- Textual: Modern TUI framework
  https://github.com/Textualize/textual

- Pyfiglet: ASCII art generation
  https://github.com/pwaller/pyfiglet
  Font Preview: http://www.figlet.org/examples.html

- PyYAML: YAML file parsing
  https://pyyaml.org/

- Rich: Terminal formatting
  https://github.com/Textualize/rich

- GitPython: Git operations
  https://github.com/gitpython-developers/GitPython

License: MIT


