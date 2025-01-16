import os
import shutil
from pathlib import Path
import git

def setup_test_environment():
    """Set up the test environment with local repos and scripts."""
    test_root = Path("tests")
    deployment_yamls = test_root / "deployment_yamls"
    test_repos = test_root / "test_repos"
    
    # Create directories if they don't exist
    for dir_path in [deployment_yamls, test_repos]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Define test repos and their scripts
    test_repo_configs = {
        "repo1": {
            "script_name": "hello.sh",
            "script_content": """#!/bin/bash
echo "Starting hello script"
echo "TEST_VAR is: $TEST_VAR"
echo "AWS Profile is: $AWS_PROFILE"
echo "Hello script completed successfully"
"""
        },
        "repo2": {
            "script_name": "world.sh",  # Match the script name in step2.yml
            "script_content": """#!/bin/bash
echo "Starting world script"
echo "TEST_VAR is: $TEST_VAR"
echo "AWS Profile is: $AWS_PROFILE"
echo "World script completed successfully"
"""
        }
    }
    
    # Set up each repository
    for repo_name, config in test_repo_configs.items():
        repo_path = test_repos / repo_name
        if not repo_path.exists():
            repo_path.mkdir(parents=True, exist_ok=True)
        
        # Create scripts directory and add test script
        scripts_dir = repo_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test script
        script_path = scripts_dir / config["script_name"]
        script_path.write_text(config["script_content"])
        script_path.chmod(0o755)  # Make executable
        
        # Initialize git repository if not already initialized
        if not (repo_path / '.git').exists():
            repo = git.Repo.init(repo_path)
            # Add all files and commit
            repo.index.add([str(script_path.relative_to(repo_path))])
            repo.index.commit(f"Initial commit with {config['script_name']}")

if __name__ == "__main__":
    setup_test_environment()
    print("Test environment setup complete!") 