from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from textual.screen import Screen
from textual import events
from rich.console import RenderableType
import asyncio
from textual.containers import Container
from textual.widgets import Static
import yaml
from pathlib import Path
import pyfiglet
from textual.app import ComposeResult
from zd_base import BaseScreen
from textual.binding import Binding

class ZDSplashScreen(BaseScreen):
    """A stylish splash screen for ZenDeploy."""
    
    # Only allow quit and back on splash screen
    DISABLED_BINDINGS = {"add_file", "review", "help", "deploy"}

    def __init__(self):
        super().__init__()
        self.theme = self._load_theme()

    def _load_theme(self) -> dict:
        """Load theme configuration from theme.yml."""
        theme_path = Path("theme.yml")
        if theme_path.exists():
            with open(theme_path) as f:
                return yaml.safe_load(f)
        return {}

    def _generate_ascii_art(self, text: str) -> str:
        """Generate ASCII art from text using pyfiglet."""
        # Get box style from theme
        box_style = self.theme.get("splash", {}).get("box", {}).get("style", "double")
        box_chars = {
            "single": ("┌", "┐", "└", "┘", "─", "│"),
            "double": ("╔", "╗", "╚", "╝", "═", "║"),
            "heavy": ("┏", "┓", "┗", "┛", "━", "┃")
        }[box_style]

        # Generate ASCII art
        font = self.theme.get("splash", {}).get("font", "big")
        ascii_art = pyfiglet.figlet_format(text, font=font)
        
        # Split into lines and clean up empty lines
        lines = [line for line in ascii_art.split('\n') if line.strip()]
        max_width = max(len(line) for line in lines)
        
        # Add consistent padding (2 lines top and bottom)
        padding = 2
        
        # Build result with box and padding
        result = [box_chars[0] + box_chars[4] * (max_width + 4) + box_chars[1]]
        
        # Top padding
        for _ in range(padding):
            result.append(f"{box_chars[5]}" + " " * (max_width + 4) + f"{box_chars[5]}")
        
        # Content lines, centered
        for line in lines:
            padded_line = line.center(max_width)
            result.append(f"{box_chars[5]}  {padded_line}  {box_chars[5]}")
        
        # Bottom padding
        for _ in range(padding):
            result.append(f"{box_chars[5]}" + " " * (max_width + 4) + f"{box_chars[5]}")
        
        result.append(box_chars[2] + box_chars[4] * (max_width + 4) + box_chars[3])
        
        return "\n".join(result)

    def compose(self) -> ComposeResult:
        """Create child widgets for the splash screen."""
        # First yield the base elements (Header, Footer with branding)
        yield from super().compose()
        
        # Generate ASCII art from app_name
        title_text = self._generate_ascii_art(self.theme.get("app_name", "ZENDEPLOY"))
        
        yield Container(
            Static(title_text, classes="zd-splash-title"),
            Static(self.theme.get("description", ""), classes="zd-splash-subtitle"),
            Static(f"Version {self.theme.get('display_version', '')}", classes="zd-splash-version"),
            Static(f"By {self.theme.get('author', '')} - {self.theme.get('date', '')}", 
                  classes="zd-splash-author"),
            Static(self.theme.get("splash", {}).get("prompt", "Press any key to continue..."), 
                  classes="zd-splash-prompt"),
            id="zd-splash-content"
        )

    async def on_key(self, event: events.Key) -> None:
        """Handle key press to dismiss the splash screen."""
        self.query_one("#zd-splash-content").add_class("zd-fade-out")
        await asyncio.sleep(0.5)
        await self.app.push_screen("main") 