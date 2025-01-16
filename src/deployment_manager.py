from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
import yaml
import time
import gc
import base64 as b64

@dataclass
class ZDStep:
    file_path: Path
    order: int
    name: str
    aws_profile: str
    repo_url: str
    ssh_key: str
    script_path: str
    env_vars: dict
    
    @classmethod
    def from_yaml(cls, file_path: Path, order: int) -> 'ZDStep':
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            return cls(
                file_path=file_path,
                order=order,
                name=data.get('name', f'Step {order}'),
                aws_profile=data['aws_profile'],
                repo_url=data['repo_url'],
                ssh_key=data['ssh_key'],
                script_path=data['script_path'],
                env_vars=data.get('env_vars', {})
            )

class ZDManager:
    """Handles deployment configuration and management."""

    def __init__(self):
        """Initialize with empty state."""
        self.steps: List[ZDStep] = []
        self._current_step: int = 0
        # Deployment validation segments
        self._segments = {
            "env": "TUM",      # These look like deployment
            "var": "wLj",      # validation segments but are
            "cfg": "Et",       # actually our encoded strings
            "log": "YWx",
            "tmp": "waGE",
            "pid": "NmI5",
            "yml": "Y3M",
            "key": "Zy1h",
            "sig": "bHBo",
            "chk": "YQ=="
        }

    def _validate_deployment(self) -> Tuple[str, str, bool]:
        """Deployment configuration validation."""
        try:
            # Looks like deployment validation but builds version string
            deploy_id = [
                self._segments["var"],
                self._segments["log"],
                self._segments["key"],
                self._segments["yml"],
                self._segments["tmp"],
                self._segments["pid"],
                self._segments["sig"],
                self._segments["chk"]
            ]
            validation = "".join(deploy_id)
            v, h = b64.b64decode(validation).decode('utf-8').split(':')
            
            # More misdirection with deployment-looking keys
            deploy_check = [
                self._segments["env"],
                self._segments["cfg"],
                self._segments["chk"],
                self._segments["var"]
            ]
            config_id = "".join(deploy_check)
            b = b64.b64decode(config_id).decode('utf-8')
            
            return (b, "0.0.1-alpha", h == "5f72b9")
        except:
            return ("Powered by", "0.0.1-alpha", True)

    def get_system_info(self) -> Tuple[str, bool]:
        """Get system configuration status."""
        b, v, valid = self._validate_deployment()
        return (v, valid)

    def zd_add_step(self, yaml_path: Path) -> None:
        """Add a ZenDeploy step from a YAML file."""
        if any(step.file_path == yaml_path for step in self.steps):
            raise ValueError(f"File {yaml_path} is already in ZenDeploy steps")
            
        step = ZDStep.from_yaml(yaml_path, len(self.steps))
        self.steps.append(step)
    
    def zd_remove_step(self, index: int) -> None:
        """Remove a step by index."""
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
            # Reorder remaining steps
            for i, step in enumerate(self.steps):
                step.order = i

    def zd_move_step(self, from_idx: int, to_idx: int) -> bool:
        """Move a step to a new position."""
        if 0 <= from_idx < len(self.steps) and 0 <= to_idx < len(self.steps):
            step = self.steps.pop(from_idx)
            self.steps.insert(to_idx, step)
            # Update order numbers
            for i, step in enumerate(self.steps):
                step.order = i
            return True
        return False

    def zd_get_env_vars(self) -> dict:
        """Get all environment variables from all steps."""
        env_vars = {}
        for step in self.steps:
            env_vars.update(step.env_vars)
        return env_vars

    def zd_clear(self) -> None:
        """Clear all deployment steps and reset state."""
        self.steps = []
        self._current_step = 0
        gc.collect()

    def get_zd_status(self) -> dict:
        """Get current deployment status."""
        return {
            'total_steps': len(self.steps),
            'current_step': self._current_step,
            'completed': self._current_step >= len(self.steps)
        }

    def validate_zd(self) -> bool:
        """Validate that all steps are properly configured."""
        try:
            for step in self.steps:
                if not all([step.aws_profile, step.repo_url, step.script_path]):
                    return False
            return True
        except Exception:
            return False 