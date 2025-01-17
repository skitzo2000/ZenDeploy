# ZenDeploy (ZD)

A Terminal User Interface (TUI) application for managing and executing AWS deployments through YAML configurations. ZenDeploy provides a streamlined way to manage deployment scripts, configure AWS environments, and execute deployments with real-time monitoring and comprehensive audit logging.

## Screenshots

| <img src="docs/assets/splash.png" width="200" alt="Splash Screen"/><br/><em>ZenDeploy Welcome Screen</em> | <img src="docs/assets/Main.png" width="200" alt="Main Interface"/><br/><em>Main interface for deployment file selection</em> |
|:---:|:---:|
| <img src="docs/assets/review.png" width="200" alt="Review Screen"/><br/><em>Deployment review and configuration screen</em> | <img src="docs/assets/deploy.png" width="200" alt="Deployment Progress"/><br/><em>Deployment execution and progress monitoring</em> |

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python src/main.py
```

For detailed setup instructions, see the [Installation Guide](docs/installation.md).

## Documentation

- [Installation Guide](docs/installation.md) - Setup and requirements
- [Configuration Guide](docs/configuration.md) - YAML configuration and theming
- [Testing Guide](docs/testing.md) - Testing and development

## Current Status

This is an alpha release with the following limitations:
- Not production-ready
- Limited functionality
- Testing framework in development
- Documentation in progress

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

See the [Testing Guide](docs/testing.md) for development setup.

## License

[MIT License](LICENSE)

## Credits

Built with:
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [PyYAML](https://pyyaml.org/) - YAML parsing
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git operations


