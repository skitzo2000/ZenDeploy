import asyncio
import tempfile
import os
from pathlib import Path
import shutil
import git
from typing import AsyncGenerator, Optional
import subprocess
from audit_logger import ZDLogger

class ZDExecutor:
    def __init__(self, zd_manager, audit_logger: ZDLogger):
        self.zd_manager = zd_manager
        self.audit_logger = audit_logger
        self.temp_dir = None
        self.current_step = None

    async def zd_prepare(self) -> bool:
        """Prepare the deployment environment."""
        try:
            # Create temporary directory for deployments
            self.temp_dir = Path(tempfile.mkdtemp(prefix="zd_"))
            await self.audit_logger.zd_log_action("zd_prepare", f"Created temp dir: {self.temp_dir}")
            return True
        except Exception as e:
            await self.audit_logger.zd_log_action("zd_prepare_error", str(e))
            return False

    async def zd_execute(self) -> AsyncGenerator[tuple[str, str], None]:
        """Execute all deployment steps and yield tuples of (formatted_output, raw_output)."""
        if not self.temp_dir:
            yield (
                "[red]Error: Deployment not prepared[/red]\n",
                "ERROR: Deployment not prepared\n"
            )
            return

        try:
            for step in self.zd_manager.steps:
                self.current_step = step
                async for output in self.zd_execute_step(step):
                    yield output  # output is already a tuple from zd_execute_step

        finally:
            # Cleanup
            await self.zd_cleanup()

    async def zd_execute_step(self, step) -> AsyncGenerator[tuple[str, str], None]:
        """Execute a single deployment step."""
        step_dir = self.temp_dir / f"step_{step.order}"
        step_dir.mkdir(exist_ok=True)
        success = False

        try:
            # Header
            yield (
                f"\n[bold blue]Step {step.order + 1}: {step.name}[/bold blue]\n",
                f"\n=== Step {step.order + 1}: {step.name} ===\n"
            )

            # Clone repository
            # Don't show the raw command yet - let zd_clone_repo handle it
            yield (
                "[yellow]Cloning repository...[/yellow]\n",
                ""  # Empty string for raw output, will be handled by zd_clone_repo
            )

            repo = await self.zd_clone_repo(step, step_dir)
            if not repo:
                error_msg = "Failed to clone repository"
                yield (
                    f"[red]✗ {error_msg}[/red]\n",
                    f"ERROR: {error_msg}\n"
                )
                return

            yield (
                "[green]✓ Repository cloned successfully[/green]\n",
                "Repository cloned successfully\n"
            )

            # Set AWS profile
            os.environ['AWS_PROFILE'] = step.aws_profile
            yield (
                f"[yellow]Setting AWS Profile to: {step.aws_profile}[/yellow]\n",
                f"$ export AWS_PROFILE={step.aws_profile}\n"
            )
            yield (
                "[green]✓ AWS Profile set[/green]\n",
                "AWS Profile set\n"
            )

            # Set environment variables
            for key, value in step.env_vars.items():
                os.environ[key] = str(value)
                yield (
                    f"[yellow]Setting {key}={value}[/yellow]\n",
                    f"$ export {key}={value}\n"
                )
            yield (
                "[green]✓ Environment variables set[/green]\n",
                "Environment variables set\n"
            )

            # Execute script
            # First, find the script in the cloned repository
            repo_script_path = step_dir / step.script_path
            if not repo_script_path.exists():
                error_msg = f"Script not found at {repo_script_path}"
                await self.audit_logger.zd_log_action("debug", f"Looking for script at: {repo_script_path}")
                await self.audit_logger.zd_log_action("debug", f"Repository directory contents: {list(step_dir.glob('**/*'))}")
                yield (
                    f"[red]✗ {error_msg}[/red]\n",
                    f"ERROR: {error_msg}\n"
                )
                await self.audit_logger.zd_log_action("step_error", error_msg)
                return

            # Make script executable
            repo_script_path.chmod(0o755)
            
            yield (
                f"[yellow]Executing script: {repo_script_path}[/yellow]\n",
                f"$ {repo_script_path}\n"
            )
            async for formatted, raw in self.zd_run_script(repo_script_path, step.name):
                yield formatted, raw

            # Only mark as successful if we get here
            success = True
            yield (
                f"[green]✓ Step {step.order + 1} completed successfully[/green]\n",
                f"=== Step {step.order + 1} Completed Successfully ===\n"
            )
            yield ("-" * 40 + "\n", "-" * 40 + "\n")

        except Exception as e:
            error_msg = f"Error in step {step.name}: {str(e)}"
            yield (
                f"[red]✗ {error_msg}[/red]\n",
                f"ERROR: {error_msg}\n"
            )
            await self.audit_logger.zd_log_action("step_error", error_msg)
            raise

        finally:
            if not success:
                yield (
                    f"[red]✗ Step {step.order + 1} failed[/red]\n",
                    f"=== Step {step.order + 1} Failed ===\n"
                )

    async def zd_clone_repo(self, step, directory: Path) -> Optional[git.Repo]:
        """Clone the git repository for a step."""
        try:
            # For local file:// repositories, handle differently
            if step.repo_url.startswith('file://'):
                # Get the absolute path of the repository
                local_path = step.repo_url.replace('file://', '')
                base_dir = Path(__file__).parent.parent
                abs_path = (base_dir / local_path).resolve()

                # Debug logging
                await self.audit_logger.zd_log_action("debug", f"Current working directory: {os.getcwd()}")
                await self.audit_logger.zd_log_action("debug", f"Base directory: {base_dir}")
                await self.audit_logger.zd_log_action("debug", f"Original path: {local_path}")
                await self.audit_logger.zd_log_action("debug", f"Resolved path: {abs_path}")
                await self.audit_logger.zd_log_action("debug", f"Target directory: {directory}")

                if not abs_path.exists():
                    error_msg = f"Repository path not found: {abs_path}"
                    await self.audit_logger.zd_log_action("error", error_msg)
                    raise ValueError(error_msg)

                # Check if it's a git repository
                git_dir = abs_path / '.git'
                if git_dir.exists():
                    await self.audit_logger.zd_log_action("debug", f"Found .git directory at {git_dir}")
                else:
                    await self.audit_logger.zd_log_action("debug", "No .git directory found")

                # Use the absolute path for the clone command
                repo_path = str(abs_path)
                clone_cmd = f"$ git clone {repo_path} {directory}"
                
                # Log the command
                await self.audit_logger.zd_log_action("command", clone_cmd)

                try:
                    # Attempt the clone
                    repo = git.Repo.clone_from(
                        url=repo_path,
                        to_path=str(directory),
                        multi_options=['--no-hardlinks']
                    )

                    await self.audit_logger.zd_log_action(
                        "success",
                        f"Successfully cloned {repo_path} to {directory}"
                    )
                    return repo

                except git.exc.GitCommandError as git_error:
                    error_msg = f"Git clone failed: {str(git_error)}"
                    await self.audit_logger.zd_log_action("error", error_msg)
                    raise

            else:
                # Remote repository handling
                clone_cmd = f"$ git clone {step.repo_url} {directory}"
                await self.audit_logger.zd_log_action("clone_attempt", clone_cmd)
                
                git_ssh_cmd = f'ssh -i {step.ssh_key}'
                env = os.environ.copy()
                env['GIT_SSH_COMMAND'] = git_ssh_cmd

                repo = git.Repo.clone_from(
                    url=step.repo_url,
                    to_path=str(directory),
                    env=env
                )
                return repo

        except Exception as e:
            error_msg = f"Repository clone failed: {str(e)}"
            await self.audit_logger.zd_log_action("repo_clone_error", error_msg)
            # Log the full exception details for debugging
            import traceback
            await self.audit_logger.zd_log_action("error", f"Full error: {traceback.format_exc()}")
            return None

    async def zd_run_script(self, script_path: Path, step_name: str) -> AsyncGenerator[tuple[str, str], None]:
        """Execute a deployment script and yield tuples of (formatted_output, raw_output)"""
        try:
            script_path.chmod(0o755)
            process = await asyncio.create_subprocess_exec(
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                output = line.decode().strip()
                await self.audit_logger.zd_log_output(step_name, "execute", output)
                yield f"{output}\n", f"{output}\n"

            await process.wait()

            if process.returncode != 0:
                error = await process.stderr.read()
                error_msg = error.decode().strip()
                await self.audit_logger.zd_log_output(step_name, "error", error_msg)
                yield (
                    f"[red]Script execution failed: {error_msg}[/red]\n",
                    f"ERROR: Script execution failed: {error_msg}\n"
                )

        except Exception as e:
            error_msg = f"Script execution error: {str(e)}"
            await self.audit_logger.zd_log_output(step_name, "error", error_msg)
            yield (
                f"[red]{error_msg}[/red]\n",
                f"ERROR: {error_msg}\n"
            )

    async def zd_cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            await self.audit_logger.zd_log_action("zd_cleanup", f"Removed temp dir: {self.temp_dir}") 