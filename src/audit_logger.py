import asyncio
from datetime import datetime
from pathlib import Path
import os

class ZDLogger:
    """Session-based audit logger that handles both action logging and deployment output."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = int(datetime.now().timestamp())
        self.username = os.getenv('USER', 'unknown')
        self.log_file = self.log_dir / f"{self.username}_{self.session_id}_zd_session.log"
        
        # Create session log with header
        with open(self.log_file, "w") as f:
            f.write(f"=== ZenDeploy Session Started: {datetime.now().isoformat()} ===\n")
            f.write(f"User: {self.username}\n")
            f.write("=" * 50 + "\n\n")

    async def zd_log_action(self, action: str, details: str = "") -> None:
        """Log an action to the session log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[ACTION] {timestamp} | {self.username} | {action}"
        if details:
            log_entry += f" | {details}"
        log_entry += "\n"
        
        async with asyncio.Lock():
            with open(self.log_file, "a") as f:
                f.write(log_entry)

    async def zd_log_output(self, step_name: str, command: str, output: str) -> None:
        """Log detailed deployment output to the session log."""
        timestamp = datetime.now().isoformat()
        deployment_log = (
            f"\n[ZD] Step: {step_name}\n"
            f"Timestamp: {timestamp}\n"
            f"Command: {command}\n"
            f"Output:\n{output}\n"
            f"{'-' * 50}\n"
        )
        
        async with asyncio.Lock():
            with open(self.log_file, "a") as f:
                f.write(deployment_log)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Add session end marker when the logger is closed."""
        async with asyncio.Lock():
            with open(self.log_file, "a") as f:
                f.write(f"\n=== ZenDeploy Session Ended: {datetime.now().isoformat()} ===\n")
                if exc_type:
                    f.write(f"Session ended with error: {exc_val}\n")
                f.write("=" * 50 + "\n") 