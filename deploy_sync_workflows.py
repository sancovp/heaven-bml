#!/usr/bin/env python3
"""
Deploy sync workflows to test the meta-repo sync system.

This script will:
1. Copy sync-sender.yml to a private sub-repo
2. Copy sync-receiver.yml and archive-closer.yml to the meta-repo
3. Guide you through setting up the required secrets
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, capture=False):
    """Run a shell command."""
    print(f"Running: {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        return subprocess.run(cmd, shell=True).returncode == 0

def main():
    # Get the GitHub token from environment or prompt
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        print("Please set GITHUB_TOKEN environment variable with your PAT")
        print("export GITHUB_TOKEN='your_pat_here'")
        return 1
    
    # Configuration
    meta_repo = "sancovp/private_heaven_meta_workspace"
    
    print("=== Meta-Repo Sync Deployment Script ===\n")
    
    # Get sub-repo to test with
    sub_repo = input("Enter the private sub-repo to sync FROM (e.g., sancovp/heaven-base-private): ").strip()
    if not sub_repo:
        print("Sub-repo is required!")
        return 1
    
    # Paths
    script_dir = Path(__file__).parent
    workflows_dir = script_dir / "github_workflows"
    
    print(f"\nWill set up sync between:")
    print(f"  Sub-repo: {sub_repo}")
    print(f"  Meta-repo: {meta_repo}")
    
    confirm = input("\nContinue? (y/n): ").lower()
    if confirm != 'y':
        return 0
    
    # Create temp directory for operations
    temp_dir = Path("/tmp/sync_workflow_deploy")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Deploy to sub-repo
        print(f"\n=== Deploying to {sub_repo} ===")
        
        # Clone sub-repo
        sub_repo_dir = temp_dir / "sub_repo"
        if sub_repo_dir.exists():
            shutil.rmtree(sub_repo_dir)
        
        clone_url = f"https://{token}@github.com/{sub_repo}.git"
        if not run_command(f"git clone {clone_url} {sub_repo_dir}"):
            print(f"Failed to clone {sub_repo}")
            return 1
        
        # Create workflows directory
        sub_workflows = sub_repo_dir / ".github" / "workflows"
        sub_workflows.mkdir(parents=True, exist_ok=True)
        
        # Copy sync-sender.yml
        shutil.copy(workflows_dir / "sync-sender.yml", sub_workflows / "sync-sender.yml")
        
        # Commit and push
        os.chdir(sub_repo_dir)
        run_command("git add .github/workflows/sync-sender.yml")
        run_command('git commit -m "Add sync-sender workflow for meta-repo sync"')
        run_command("git push")
        
        print(f"✓ Deployed sync-sender.yml to {sub_repo}")
        
        # Deploy to meta-repo
        print(f"\n=== Deploying to {meta_repo} ===")
        
        # Clone meta-repo
        meta_repo_dir = temp_dir / "meta_repo"
        if meta_repo_dir.exists():
            shutil.rmtree(meta_repo_dir)
        
        clone_url = f"https://{token}@github.com/{meta_repo}.git"
        if not run_command(f"git clone {clone_url} {meta_repo_dir}"):
            print(f"Failed to clone {meta_repo}")
            return 1
        
        # Create workflows directory
        meta_workflows = meta_repo_dir / ".github" / "workflows"
        meta_workflows.mkdir(parents=True, exist_ok=True)
        
        # Copy receiver workflows
        shutil.copy(workflows_dir / "sync-receiver.yml", meta_workflows / "sync-receiver.yml")
        shutil.copy(workflows_dir / "archive-closer.yml", meta_workflows / "archive-closer.yml")
        
        # Commit and push
        os.chdir(meta_repo_dir)
        run_command("git add .github/workflows/")
        run_command('git commit -m "Add sync receiver and archive closer workflows"')
        run_command("git push")
        
        print(f"✓ Deployed sync-receiver.yml and archive-closer.yml to {meta_repo}")
        
        # Setup instructions
        print("\n=== Next Steps ===")
        print(f"\n1. In {sub_repo} settings:")
        print(f"   - Add secret 'META_REPO_TOKEN' with value: {token[:10]}...")
        print(f"   - Add variable 'META_REPO_NAME' with value: {meta_repo}")
        
        print(f"\n2. In {meta_repo} settings:")
        print(f"   - Add secret 'META_REPO_TOKEN' with value: {token[:10]}...")
        
        print("\n3. Test the sync:")
        print(f"   - Create an issue in {sub_repo}")
        print(f"   - Check {meta_repo} for the wrapper issue")
        print(f"   - Add 'status-archived' label in meta to close original")
        
        print("\n✓ Deployment complete!")
        
    finally:
        # Cleanup
        os.chdir(script_dir)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())