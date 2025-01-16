from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Label
from textual.binding import Binding
from rich.text import Text
from typing import Dict, Set
from deployment_manager import ZDManager

class ZDFooter(Footer):
    DEFAULT_CSS = """
    ZDFooter {
        background: $primary;
        color: $text;
        height: 1;
        dock: bottom;
        padding: 0;
        layout: horizontal;
    }
    """

    def _process_cfg(self):
        if not hasattr(self.app, 'zd_manager'):
            mgr = ZDManager()
            return mgr._validate_deployment()
        return self.app.zd_manager._validate_deployment()

    def compose(self) -> ComposeResult:
        yield Label(self.screen.key_text if hasattr(self.screen, 'key_text') else "", 
                   id="footer-keys", classes="footer--key")
        
        cfg = self._process_cfg()
        yield Label(Text.assemble(
            (f"{cfg[0]} ", "dim white"),
            ("ZenDeploy ", "bright_blue"),
            (f"v{cfg[1]}", "dim white" if cfg[2] else "red")
        ), id="zd-branding", classes="right-aligned")

class BaseScreen(Screen):
    """Base screen class with common bindings and branding."""
    
    # Define bindings directly - this is more consistent with Textual's approach
    BINDINGS = [
        Binding("ctrl+q", "app.quit", "Quit", show=True),
        Binding("ctrl+a", "include_file", "Add File", show=True),
        Binding("ctrl+r", "review_deployment", "Review", show=True),
        Binding("ctrl+h", "show_help", "Help", show=True),
        Binding("escape", "pop_screen", "Back", show=True),
        Binding("ctrl+d", "deploy", "Deploy", show=True),
    ]

    # Override in subclasses to disable specific bindings
    DISABLED_BINDINGS: Set[str] = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_bindings()
        self._update_key_text()

    def _update_bindings(self) -> None:
        """Update available bindings based on DISABLED_BINDINGS."""
        self.BINDINGS = [
            binding for binding in self.__class__.BINDINGS
            if binding.key not in [
                b.key for b in self.__class__.BINDINGS
                if b.action.split('.')[-1] in self.DISABLED_BINDINGS
            ]
        ]

    def _update_key_text(self) -> None:
        """Update the key_text property based on enabled bindings."""
        # Filter out bindings that are disabled
        active_bindings = [
            binding for binding in self.BINDINGS
            if binding.action.split('.')[-1] not in self.DISABLED_BINDINGS
            and binding.show
        ]
        
        # Create the key text string with new format
        key_texts = []
        for binding in active_bindings:
            # Remove 'ctrl+' from the key display and just use '^'
            key_display = binding.key.replace('ctrl+', '')
            # Format as "Description ^+key"
            key_texts.append(f"{binding.description} ^{key_display}")
        
        # Join with pipe separator, but don't add pipe after last item
        self.key_text = " | ".join(key_texts)

    def compose(self) -> ComposeResult:
        yield Header()
        yield ZDFooter()

    async def _on_key(self, event) -> None:
        """Handle key events and check if action is allowed."""
        await super()._on_key(event)
        
        # Get the action from the binding
        action = next((b.action.split('.')[-1] for b in self.__class__.BINDINGS 
                      if b.key == event.key), None)
        
        if action in self.DISABLED_BINDINGS:
            command_name = next((b.description for b in self.__class__.BINDINGS 
                               if b.action.split('.')[-1] == action), action)
            self.app.notify_warning(f"'{command_name}' is not available on this screen")
            event.prevent_default()
            event.stop()

    # Action handlers with improved notifications
    async def action_include_file(self) -> None:
        """Add file to deployment."""
        if "add_file" in self.DISABLED_BINDINGS:
            return
        self.notify(
            "Use this command to add YAML files to your deployment", 
            severity="information",
            timeout=3
        )

    async def action_review_deployment(self) -> None:
        """Review deployment configuration."""
        if "review" in self.DISABLED_BINDINGS:
            return
        self.notify(
            "Use this command to review your deployment configuration", 
            severity="information",
            timeout=3
        )

    async def action_show_help(self) -> None:
        """Show help information."""
        if "help" in self.DISABLED_BINDINGS:
            return
        self.notify(
            "Displaying help information...", 
            severity="information",
            timeout=2
        )

    async def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        if "back" in self.DISABLED_BINDINGS:
            return
        await self.app.pop_screen()

    async def action_deploy(self) -> None:
        """Start deployment process."""
        if "deploy" in self.DISABLED_BINDINGS:
            return
        self.notify(
            "Use this command to start the deployment process", 
            severity="information",
            timeout=3
        ) 