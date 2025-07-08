#\!/usr/bin/env python3
"""
HEAVEN BML System - Workflow Installation Script
Installs BML GitHub workflows into any repository
"""

import os
import argparse
import subprocess
import shutil
from pathlib import Path


def create_github_workflows_directory(repo_path: str):
    """Create .github/workflows directory if it doesn't exist"""
    workflows_dir = Path(repo_path) / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    return workflows_dir


def install_workflow_file(source_file: str, target_dir: Path, repo_name: str = None):
    """Install a workflow file with repo-specific customization"""
    source_path = Path(__file__).parent.parent / "github_workflows" / source_file
    target_path = target_dir / source_file
    
    if source_path.exists():
        # Read template
        with open(source_path, 'r') as f:
            content = f.read()
        
        # Replace placeholders
        if repo_name:
            content = content.replace("{{REPO_NAME}}", repo_name)
        
        # Write to target
        with open(target_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Installed: {source_file}")
        return True
    else:
        print(f"❌ Source not found: {source_file}")
        return False


def install_bml_workflows(repo_path: str, repo_name: str = None):
    """Install all BML workflows into a repository"""
    print(f"Installing HEAVEN BML workflows into: {repo_path}")
    
    # Create workflows directory
    workflows_dir = create_github_workflows_directory(repo_path)
    
    # List of workflow files to install
    workflow_files = [
        "auto-label-issues.yml",
        "project-automation.yml", 
        "promote-idea-to-issue.yml",
        "bml-automation.yml",
        "private-release.yml",
        "public-release.yml"
    ]
    
    installed_count = 0
    for workflow_file in workflow_files:
        if install_workflow_file(workflow_file, workflows_dir, repo_name):
            installed_count += 1
    
    print(f"\n🎉 Successfully installed {installed_count}/{len(workflow_files)} workflows")
    
    # Create ideas directory
    ideas_dir = Path(repo_path) / "ideas"
    ideas_dir.mkdir(exist_ok=True)
    
    # Create sample idea file
    sample_idea = ideas_dir / "welcome-to-bml.md"
    if not sample_idea.exists():
        with open(sample_idea, 'w') as f:
            f.write("""# Welcome to HEAVEN BML System\!

This idea will be automatically converted to a GitHub issue by the BML workflows.

## What is BML?

Build-Measure-Learn project management using GitHub's native features:
- Tree notation priorities (priority-1.2.3...)
- Automated kanban workflow
- AI agent integration
- Continuous improvement cycles

## Next Steps

1. Delete this file or commit it to trigger issue creation
2. Create your own ideas in markdown files
3. Use the BML Python functions to integrate with your AI agents

**Powered by HEAVEN BML System**
""")
    
    print(f"✅ Created ideas directory and sample file")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Install HEAVEN BML workflows")
    parser.add_argument("--repo", "-r", help="Repository path (default: current directory)", default=".")
    parser.add_argument("--repo-name", "-n", help="Repository name for customization (owner/repo)")
    parser.add_argument("--github-url", "-u", help="Create GitHub repository and install")
    
    args = parser.parse_args()
    
    print("HEAVEN BML System - Workflow Installer")
    print("=" * 50)
    
    repo_path = os.path.abspath(args.repo)
    
    if args.github_url:
        print(f"Creating GitHub repository: {args.github_url}")
        # TODO: Add GitHub repo creation logic
        print("GitHub repo creation not yet implemented")
        return
    
    if not os.path.exists(repo_path):
        print(f"❌ Repository path does not exist: {repo_path}")
        return
    
    try:
        success = install_bml_workflows(repo_path, args.repo_name)
        
        if success:
            print("\n🚀 BML System installation complete\!")
            print("\nNext steps:")
            print("1. Commit the new .github/workflows to enable automation")
            print("2. Install BML Python functions: pip install heaven-bml-system")
            print("3. Integrate with your AI agents using the wrapper functions")
            print("\n📚 Documentation: https://github.com/sancovp/heaven-bml-system")
            print("\n**Powered by HEAVEN BML System**")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")


if __name__ == "__main__":
    main()
