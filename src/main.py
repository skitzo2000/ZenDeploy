from textual.app import App
from textual.widgets import Header, Footer, Static, DirectoryTree, DataTable, Button, RichLog, Label
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
from textual.message import Message
from textual.app import ComposeResult
from pathlib import Path
import yaml
import time
from deployment_manager import ZDManager
from deployment_executor import ZDExecutor
from audit_logger import ZDLogger
import asyncio
from zd_base import BaseScreen
from splash_screen import ZDSplashScreen
from rich.text import Text
from enum import Enum
from textual import events

class ZDScreens(str, Enum):
    """Screen identifiers for ZenDeploy."""
    MAIN = "main"
    REVIEW = "review"
    PROGRESS = "progress"  # Changed from zd_progress
    ABOUT = "about"
    SPLASH = "splash"

class AboutScreen(BaseScreen):
    """About screen only allows quit and back."""
    DISABLED_BINDINGS = {"add_file", "review", "help", "deploy"}

    def compose(self) -> ComposeResult:
        yield from super().compose()  # This ensures Header and Footer
        with Container(id="about-modal"):
            with open("theme.yml", "r") as f:
                theme = yaml.safe_load(f)
            yield Static(f"# {theme['app_name']}")
            yield Static(f"Version: {theme['display_version']}")
            yield Static(f"Author: {theme['author']}")
            yield Static(f"Date: {theme['date']}")
            yield Button("Close", variant="primary", id="close-about")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-about":
            self.app.pop_screen()

class ReviewScreen(BaseScreen):
    """Review screen for deployment steps."""
    
    # Only allow back, deploy, and quit on review screen
    DISABLED_BINDINGS = {"add_file", "review", "help"}

    def __init__(self, manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zd_manager = manager

    def compose(self) -> ComposeResult:
        """Create child widgets for the review screen."""
        # Get base components (Header and Footer)
        yield from super().compose()
        
        # Review screen content
        yield Container(
            Container(
                Horizontal(
                    Vertical(
                        Static("Deployment Preview", id="preview-title"),
                        Container(id="preview-list", classes="scrollable"),
                        id="preview-pane"
                    ),
                    Vertical(
                        Static("Environment Variables", id="env-title"),
                        Container(id="env-list", classes="scrollable"),
                        id="env-pane"
                    ),
                    id="top-panes"
                ),
                id="top-section"
            ),
            id="review-container"
        )

    def on_mount(self) -> None:
        """Populate the review screen with deployment information."""
        preview_container = self.query_one("#preview-list")
        env_container = self.query_one("#env-list")
        
        # Clear existing content
        preview_container.remove_children()
        env_container.remove_children()
        
        # Get fresh state from app's deployment manager
        steps = self.app.zd_manager.steps
        
        if steps:
            # Create deployment preview in left pane
            preview_container.mount(Static("Deployment Steps Summary:", classes="preview-header"))
            preview_container.mount(Static("-" * 40, classes="preview-separator"))
            
            for i, step in enumerate(steps, 1):
                preview_container.mount(Static(f"Step {i}: {step.name}", classes="preview-step"))
                preview_container.mount(Static(f"  File: {step.file_path}", classes="preview-detail"))
                preview_container.mount(Static(f"  Script: {step.script_path}", classes="preview-detail"))
                preview_container.mount(Static("", classes="preview-spacer"))

            # Populate environment variables in right pane
            for step in steps:
                env_container.mount(Static(f"[bold]{step.name}:[/bold]", classes="env-header"))
                
                # Add all attributes except file_path and order
                env_vars = {
                    "AWS Profile": step.aws_profile,
                    "Repository": step.repo_url,
                    "SSH Key": step.ssh_key,
                    "Script": step.script_path,
                }
                for key, value in env_vars.items():
                    env_container.mount(Static(f"  {key}: {value}", classes="env-item"))
                
                # Add environment variables from the step
                if step.env_vars:
                    env_container.mount(Static("  Environment Variables:", classes="env-subheader"))
                    for key, value in step.env_vars.items():
                        env_container.mount(Static(f"    {key}: {value}", classes="env-item"))
        else:
            preview_container.mount(Static("No steps to preview"))
            env_container.mount(Static("No deployment steps found"))

    async def action_pop_screen(self) -> None:
        """Handle escape key."""
        await self.app.pop_screen()

    async def action_deploy(self) -> None:
        """Handle deployment action."""
        await self.app.push_screen(ZDScreens.PROGRESS)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

class ZDProgressScreen(BaseScreen):
    """Progress screen only allows quit and back."""
    DISABLED_BINDINGS = {"add_file", "review", "help", "deploy"}

    """Screen to show deployment progress with both formatted and raw output."""
    
    SCREEN_BINDINGS = [
        Binding("escape", "pop_screen", "Back", show=True),
    ]

    def __init__(self, manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zd_manager = manager

    def compose(self) -> ComposeResult:
        """Create child widgets for the progress screen."""
        # Get base components (Header and Footer)
        yield from super().compose()
        
        # Progress screen content
        yield Container(
            Vertical(
                Static("ZenDeploy in Progress", id="progress-title"),
                Static("", id="current-step", classes="status-text"),
                Static("", id="status", classes="status-text"),
                id="status-section"
            ),
            Horizontal(
                Vertical(
                    Static("Formatted Output:", id="formatted-title"),
                    Container(
                        RichLog(id="formatted-log", markup=True, highlight=True),
                        id="formatted-container"
                    ),
                    id="formatted-log-section"
                ),
                Vertical(
                    Static("Raw Output:", id="raw-title"),
                    Container(
                        RichLog(id="raw-log"),
                        id="raw-container"
                    ),
                    id="raw-log-section"
                ),
                id="log-section"
            ),
            Static("", id="progress-bar"),
            id="zd-container"
        )

    def on_mount(self) -> None:
        """Start the deployment process when the screen is mounted."""
        self.run_worker(self.start_deployment())

    async def start_deployment(self) -> None:
        """Start the deployment process."""
        formatted_log = self.query_one("#formatted-log")
        raw_log = self.query_one("#raw-log")
        status = self.query_one("#status")
        current_step = self.query_one("#current-step")
        progress = self.query_one("#progress-bar")

        try:
            if self.app.zd_manager.steps:
                total_steps = len(self.app.zd_manager.steps)
                success = True  # Track overall success
                
                for i, step in enumerate(self.app.zd_manager.steps, 1):
                    progress_pct = (i / total_steps) * 100
                    progress.update(f"[progress.bar]{progress_pct:.0f}%")
                    current_step.update(f"Processing step {i} of {total_steps}: [bold]{step.name}[/bold]")
                    
                    try:
                        executor = ZDExecutor(self.app.zd_manager, self.app.audit_logger)
                        if not await executor.zd_prepare():
                            success = False
                            formatted_log.write("[red]Failed to prepare deployment environment[/red]\n")
                            status.update("[bold red]ZenDeploy preparation failed[/bold red]")
                            return

                        async for formatted_output, raw_output in executor.zd_execute():
                            formatted_log.write(formatted_output)
                            raw_log.write(raw_output)
                            if "failed" in raw_output.lower():
                                success = False

                    except Exception as step_error:
                        success = False
                        formatted_log.write(f"[red]✗ Step {i} failed: {str(step_error)}[/red]\n")
                        raw_log.write(f"ERROR: Step {i} failed: {str(step_error)}\n")
                        status.update(f"[bold red]ZenDeploy failed at step {i}[/bold red]")
                        return

                # Final status update based on overall success
                if success:
                    status.update("[bold green]ZenDeploy completed successfully![/bold green]")
                else:
                    status.update("[bold red]ZenDeploy completed with errors![/bold red]")
                progress.update("[progress.bar]100%")
            else:
                status.update("[bold red]No steps found![/bold red]")
                formatted_log.write("[red]Error: No steps to process[/red]\n")
                raw_log.write("Error: No steps to process\n")

        except Exception as e:
            status.update(f"[bold red]ZenDeploy failed: {str(e)}[/bold red]")
            formatted_log.write(f"[red]Error: {str(e)}[/red]\n")
            raw_log.write(f"Error: {str(e)}\n")

    async def action_pop_screen(self) -> None:
        """Handle escape key."""
        await self.app.pop_screen()

class MainScreen(BaseScreen):
    """Main screen with file browser and YAML viewer."""
    
    # Disable back and deploy on main screen
    DISABLED_BINDINGS = {"back", "deploy"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_file = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Get the base components (Header and Footer)
        yield from super().compose()
        
        # Main content area
        with Container(id="main-container"):
            with Horizontal(id="content-area"):
                yield DirectoryTree("./", id="file-browser")
                with Vertical(id="yaml-panel"):
                    yield DataTable(id="yaml-viewer")

    def on_mount(self) -> None:
        """Handle the screen mount event."""
        # Hide the YAML panel initially
        self.query_one("#yaml-panel").styles.display = "none"
        self.app.sub_title = "Deployment Manager"

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection in the directory tree."""
        try:
            # Show the YAML panel
            yaml_panel = self.query_one("#yaml-panel")
            yaml_panel.styles.display = "block"

            # Update the current file
            self.current_file = event.path

            # If it's a YAML file, show the content
            if str(event.path).endswith(('.yml', '.yaml')):
                with open(event.path) as f:
                    yaml_content = yaml.safe_load(f)
                
                # Update the DataTable with YAML content
                table = self.query_one(DataTable)
                table.clear()
                table.add_column("Key", width=30)
                table.add_column("Value")
                
                # Add the YAML data to the table
                def add_yaml_to_table(data, prefix=''):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, (dict, list)):
                                add_yaml_to_table(value, f"{prefix}{key}.")
                            else:
                                table.add_row(f"{prefix}{key}", str(value))
                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            if isinstance(item, (dict, list)):
                                add_yaml_to_table(item, f"{prefix}[{i}].")
                            else:
                                table.add_row(f"{prefix}[{i}]", str(item))
                
                add_yaml_to_table(yaml_content)
            else:
                yaml_panel.styles.display = "none"
                self.notify("Not a YAML file", severity="warning")

        except Exception as e:
            self.notify(f"Error loading file: {str(e)}", severity="error")
            yaml_panel.styles.display = "none"

    async def action_include_file(self) -> None:
        """Include the selected file in deployment."""
        if "add_file" in self.DISABLED_BINDINGS:
            return
        
        tree = self.query_one("#file-browser")
        if not tree.cursor_node:
            self.app.notify_warning("Please select a YAML file in the file browser first")
            return

        file_path = str(tree.cursor_node.data.path)
        if not file_path.endswith(('.yml', '.yaml')):
            self.app.notify_warning("Selected file must be a YAML file (.yml or .yaml)")
            return

        try:
            path = Path(file_path)
            self.app.zd_manager.zd_add_step(path)
            await self.app.zd_save_log("included_file", str(path))
            self.app.notify_success(
                f"Added '{path.name}' to deployment steps ({len(self.app.zd_manager.steps)} total)"
            )
        except ValueError as e:
            self.app.notify_warning(str(e))
        except Exception as e:
            self.app.notify_error(f"Error adding file: {str(e)}")

    async def action_review_deployment(self) -> None:
        """Review the current ZD steps."""
        if "review" in self.DISABLED_BINDINGS:
            return
        
        if not self.app.zd_manager.steps:
            self.app.notify_warning("No deployment steps to review. Add some YAML files first!")
            return

        self.app.notify_info("Opening deployment review screen...")
        try:
            await self.app.push_screen(ZDScreens.REVIEW)
        except Exception as e:
            self.app.notify_error(f"Error opening review screen: {str(e)}")

    async def action_show_help(self) -> None:
        """Show help information and about details."""
        if "help" in self.DISABLED_BINDINGS:
            return

        try:
            with open("theme.yml", "r") as f:
                theme = yaml.safe_load(f)
            
            help_text = f"""
{theme['app_name']} v{theme['display_version']}
by {theme['author']}

Available Commands:
-----------------
Ctrl+A: Add a YAML file to deployment
Ctrl+R: Review deployment steps
Ctrl+H: Show this help screen
Ctrl+Q: Quit application
ESC:   Go back/close screens

About:
------
{theme.get('description', 'A deployment management tool.')}
            """
            self.notify(help_text, severity="information", timeout=20)
        except Exception as e:
            self.notify(f"Error showing help: {str(e)}", severity="error")

class ZDApp(App):
    """Main application class."""
    
    CSS_PATH = str(Path(__file__).parent.parent / "style.css")
    TITLE = "ZenDeploy"

    def __init__(self):
        super().__init__()
        self.zd_manager = ZDManager()
        self.audit_logger = ZDLogger()
        self.screens = {
            ZDScreens.MAIN: MainScreen(),
            ZDScreens.REVIEW: ReviewScreen(self.zd_manager),
            ZDScreens.PROGRESS: ZDProgressScreen(self.zd_manager),
            ZDScreens.ABOUT: AboutScreen(),
            ZDScreens.SPLASH: ZDSplashScreen(),
        }

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Register all screens
        for name, screen in self.screens.items():
            self.install_screen(screen, name)
        
        # Start with splash screen
        await self.push_screen(ZDScreens.SPLASH)

    async def zd_save_log(self, action: str, details: str = "") -> None:
        """Log an action with the audit logger."""
        try:
            await self.audit_logger.zd_log_action(action, details)
        except Exception as e:
            self.notify_error(f"Logging error: {str(e)}")

    def notify_info(self, message: str, timeout: int = 3) -> None:
        """Show an information notification."""
        if self.screen:  # Check if screen exists
            self.screen.notify(message, severity="information", timeout=timeout)

    def notify_warning(self, message: str, timeout: int = 3) -> None:
        """Show a warning notification."""
        if self.screen:  # Check if screen exists
            self.screen.notify(message, severity="warning", timeout=timeout)

    def notify_error(self, message: str, timeout: int = 5) -> None:
        """Show an error notification."""
        if self.screen:  # Check if screen exists
            self.screen.notify(message, severity="error", timeout=timeout)

    def notify_success(self, message: str, timeout: int = 3) -> None:
        """Show a success notification."""
        if self.screen:  # Check if screen exists
            self.screen.notify(f"✓ {message}", severity="information", timeout=timeout)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'audit_logger'):
            await self.audit_logger.__aexit__(exc_type, exc_val, exc_tb)

if __name__ == "__main__":
    app = ZDApp()
    app.run() 