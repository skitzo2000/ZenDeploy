from textual.screen import Screen
from textual.widgets import DataTable, Button, Header, Footer, Log, Label, Static
from textual.containers import Vertical, Horizontal
from deployment_manager import ZDManager
from deployment_executor import ZDExecutor

class ReviewScreen(Screen):
    def __init__(self, zd_manager: ZDManager):
        super().__init__()
        self.zd_manager = zd_manager

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

    def compose(self):
        yield Header()
        
        with Vertical():
            # Steps Table
            yield Label("Deployment Steps", classes="section-header")
            steps_table = DataTable(id="steps-table")
            steps_table.add_column("Order")
            steps_table.add_column("Name")
            steps_table.add_column("AWS Profile")
            steps_table.add_column("Script")
            
            for step in self.zd_manager.steps:
                steps_table.add_row(
                    str(step.order + 1),
                    step.name,
                    step.aws_profile,
                    step.script_path
                )
            yield steps_table

            # Environment Variables Table
            yield Label("Environment Variables", classes="section-header")
            env_table = DataTable(id="env-table")
            env_table.add_column("Variable")
            env_table.add_column("Value")
            
            for key, value in self.zd_manager.zd_get_env_vars().items():
                env_table.add_row(key, str(value))
            yield env_table

            # Action Buttons
            with Horizontal(id="action-buttons"):
                yield Button("Approve", variant="success", id="approve-zd")
                yield Button("Deny", variant="error", id="deny-zd")

        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "approve-zd":
            await self.app.zd_save_log("zd_approved")
            await self.start_zd()
        elif event.button.id == "deny-zd":
            await self.app.zd_save_log("zd_denied")
            self.app.pop_screen()
        elif event.button.id == "finish-zd":
            self.app.pop_screen()

    async def start_zd(self):
        self.query_one(Vertical).remove()
        log_widget = Log(id="zd-log")
        self.mount(log_widget)

        executor = ZDExecutor(self.zd_manager, self.app.audit_logger)
        
        if not await executor.zd_prepare():
            log_widget.write("Failed to prepare deployment environment")
            return

        async for output in executor.zd_execute():
            log_widget.write(output)

        self.mount(Button("Finish", variant="primary", id="finish-zd")) 