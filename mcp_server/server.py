"""
BML MCP Server - Build-Measure-Learn GitHub project management for AI agents
"""
import json
import base64
import requests
from enum import Enum
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError
from pydantic import BaseModel


class BMLTools(str, Enum):
    """Available BML tools for GitHub project management"""
    LIST_ISSUES = "list_issues"
    GET_ISSUE = "get_issue"
    CREATE_ISSUE = "create_issue"
    EDIT_ISSUE = "edit_issue"
    MOVE_ISSUE_ABOVE = "move_issue_above"
    MOVE_ISSUE_BELOW = "move_issue_below"
    MOVE_ISSUE_BETWEEN = "move_issue_between"
    SET_ISSUE_STATUS = "set_issue_status"
    SET_ISSUE_PRIORITY = "set_issue_priority"
    VIEW_KANBAN = "view_kanban"
    GET_KANBAN_LANE = "get_kanban_lane"
    INSTALL_BML_WORKFLOWS = "install_bml_workflows"
    CREATE_REPO_WITH_TYPE = "create_repo_with_type"
    # Ecosystem management tools
    GET_ECOSYSTEM_CONFIG = "get_ecosystem_config"
    ADD_REPO_TO_ECOSYSTEM = "add_repo_to_ecosystem"
    CREATE_ECOSYSTEM_REPO = "create_ecosystem_repo"


# Import real BML functions from heaven-bml-system package
try:
    from heaven_bml.tree_kanban import (
        get_all_prioritized_issues,
        move_issue_above,
        move_issue_below, 
        move_issue_between,
        set_issue_tree_priority,
        construct_tree_kanban
    )
    from heaven_bml.github_kanban import (
        construct_kanban_from_labels,
        view_lane
    )
    print("✅ Successfully imported real BML functions")
    USING_REAL_FUNCTIONS = True
except ImportError as e:
    print(f"⚠️ Could not import real BML functions ({e}), using stubs")
    USING_REAL_FUNCTIONS = False
    
    # Fallback stub implementations
    def get_all_prioritized_issues(repo: str) -> list:
        return [
            {"number": 1, "title": "Sample Issue 1", "labels": ["status-backlog", "priority-1"]},
            {"number": 2, "title": "Sample Issue 2", "labels": ["status-plan", "priority-2"]},
        ]
    
    def move_issue_above(issue_id: str, target_issue_id: str, repo: str) -> str:
        return f"STUB: Moved issue {issue_id} above issue {target_issue_id} in {repo}"
    
    def move_issue_below(issue_id: str, target_issue_id: str, repo: str) -> str:
        return f"STUB: Moved issue {issue_id} below issue {target_issue_id} in {repo}"
    
    def move_issue_between(issue_id: str, above_issue_id: str, below_issue_id: str, repo: str) -> str:
        return f"STUB: Moved issue {issue_id} between {above_issue_id} and {below_issue_id} in {repo}"
    
    def construct_kanban_from_labels(repo: str) -> dict:
        return {
            "backlog": [{"number": 1, "title": "Sample Issue 1"}],
            "plan": [{"number": 2, "title": "Sample Issue 2"}],
            "build": [], "measure": [], "learn": [], "blocked": [], "archived": []
        }
    
    def view_lane(repo: str, status: str) -> list:
        return [{"number": 1, "title": f"Sample issue in {status}"}]

# Import the real BML function directly
try:
    from heaven_bml.tree_kanban import set_issue_status as bml_set_issue_status
except ImportError:
    def bml_set_issue_status(repo: str, issue_number: int, status: str) -> bool:
        return False


class BMLServer:
    """
    HEAVEN Build-Measure-Learn Server with Tree Notation Priorities
    
    This server provides AI agents with sophisticated GitHub project management using:
    
    🌳 TREE NOTATION PRIORITIES:
    - Hierarchical priorities: 1 > 1.1 > 1.2 > 1.2.1 > 1.2.2 > 1.3 > 2
    - Infinite nesting allows precise task organization
    - Natural sorting: priority-1.2.3 comes before priority-1.2.4
    - Create sub-tasks by moving below parent (1.2 → 1.2.1, 1.2.2...)
    
    📋 BUILD-MEASURE-LEARN WORKFLOW:
    - backlog: Ideas and requests waiting for prioritization
    - plan: Prioritized and designed tasks ready for development  
    - build: Currently in development
    - measure: Testing, validation, getting feedback
    - learn: Analysis, insights, retrospective
    - blocked: Stuck at any stage (with reason)
    - archived: Completed work
    
    🔧 OPERATIONS:
    Use move_issue_above/below/between to create tree hierarchies.
    Use set_issue_status to progress through BML workflow.
    Use view_kanban to see complete project state with priorities.
    """
    
    def __init__(self, default_repo: str = "sancovp/heaven-base"):
        self.default_repo = default_repo
    
    def list_issues(self, repo: str = None) -> dict:
        """Get all prioritized issues for a repository"""
        repo = repo or self.default_repo
        issues = get_all_prioritized_issues(repo)
        return {"repo": repo, "issues": issues, "total": len(issues)}
    
    def get_issue(self, issue_id: str, repo: str = None) -> dict:
        """Get details for a specific issue"""
        repo = repo or self.default_repo
        
        if USING_REAL_FUNCTIONS:
            # Use GitHub CLI to get issue details
            import subprocess
            import json
            
            try:
                cmd = f'gh issue view {issue_id} --repo {repo} --json number,title,body,labels,state'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                
                # Debug JSON parsing
                try:
                    issue_data = json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error in get_issue: {e}")
                    print(f"Command output: {result.stdout[:500]}...")
                    return {"repo": repo, "issue_id": issue_id, "error": "JSON parse error"}
                
                # Extract status from labels
                status = 'backlog'  # default
                priority = 'none'
                for label in issue_data.get('labels', []):
                    if label['name'].startswith('status-'):
                        status = label['name'][7:]  # Remove 'status-' prefix
                    elif label['name'].startswith('priority-'):
                        priority = label['name'][9:]  # Remove 'priority-' prefix
                
                return {
                    "repo": repo,
                    "issue_id": issue_id,
                    "number": issue_data['number'],
                    "title": issue_data['title'],
                    "body": issue_data['body'],
                    "state": issue_data['state'],
                    "status": status,
                    "priority": priority
                }
            except subprocess.CalledProcessError:
                return {"repo": repo, "issue_id": issue_id, "error": "Issue not found"}
        else:
            return {"repo": repo, "issue_id": issue_id, "status": "placeholder"}
    
    def create_issue(self, title: str, body: str = "", labels: list = None, repo: str = None) -> dict:
        """Create a new issue"""
        repo = repo or self.default_repo
        labels = labels or ["status-backlog", "priority-medium"]
        
        if USING_REAL_FUNCTIONS:
            # Use real BML function to create GitHub issue
            from heaven_bml.github_kanban import create_github_issue_with_status
            issue_id = create_github_issue_with_status(repo, title, body, "backlog")  # No priority by default
            return {"repo": repo, "title": title, "body": body, "issue_id": issue_id, "created": True}
        else:
            # Stub implementation
            return {"repo": repo, "title": title, "body": body, "labels": labels, "created": True}
    
    def edit_issue(self, issue_id: str, title: str = None, body: str = None, repo: str = None) -> dict:
        """Edit an existing issue's title and/or body"""
        repo = repo or self.default_repo
        
        if USING_REAL_FUNCTIONS:
            import subprocess
            try:
                cmd = ["gh", "issue", "edit", str(issue_id), "--repo", repo]
                if title:
                    cmd.extend(["--title", title])
                if body:
                    cmd.extend(["--body", body])
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return {"repo": repo, "issue_id": issue_id, "updated": True, "title": title, "body": body}
            except subprocess.CalledProcessError as e:
                return {"repo": repo, "issue_id": issue_id, "error": f"Failed to edit issue: {e.stderr}"}
        else:
            # Stub implementation
            return {"repo": repo, "issue_id": issue_id, "title": title, "body": body, "updated": True}
    
    def move_issue_above(self, issue_id: str, target_issue_id: str, repo: str = None) -> str:
        """Move issue above target issue in priority"""
        repo = repo or self.default_repo
        return move_issue_above(issue_id, target_issue_id, repo)
    
    def move_issue_below(self, issue_id: str, target_issue_id: str, repo: str = None) -> str:
        """Move issue below target issue in priority"""
        repo = repo or self.default_repo
        return move_issue_below(issue_id, target_issue_id, repo)
    
    def move_issue_between(self, issue_id: str, above_issue_id: str, below_issue_id: str, repo: str = None) -> str:
        """Move issue between two other issues"""
        repo = repo or self.default_repo
        return move_issue_between(issue_id, above_issue_id, below_issue_id, repo)
    
    def set_issue_status(self, issue_id: str, status: str, repo: str = None) -> str:
        """Set issue status (backlog/plan/build/measure/learn/blocked/archived)"""
        repo = repo or self.default_repo
        success = bml_set_issue_status(repo, int(issue_id), status)
        return f"✅ Set issue #{issue_id} to status '{status}'" if success else f"❌ Failed to set issue #{issue_id} to status '{status}'"
    
    def set_issue_priority(self, issue_id: str, priority: str, repo: str = None) -> str:
        """Set tree notation priority (e.g., '1', '1.1', '1.2.3') for hierarchical task organization"""
        repo = repo or self.default_repo
        if USING_REAL_FUNCTIONS:
            success = set_issue_tree_priority(repo, int(issue_id), priority)
            if success:
                return f"✅ Set issue #{issue_id} to priority '{priority}' in {repo}"
            else:
                return f"❌ Failed to set issue #{issue_id} to priority '{priority}' in {repo}"
        else:
            return f"STUB: Set issue {issue_id} to priority {priority} in {repo}"
    
    def view_kanban(self, repo: str = None) -> dict:
        """Get complete kanban board view with tree priority sorting"""
        repo = repo or self.default_repo
        kanban = construct_tree_kanban(repo)
        
        def format_issue_with_priority(issue):
            """Format issue with priority and tree indentation"""
            priority = None
            for label in issue.labels:
                if label.startswith('priority-'):
                    priority = label[9:]  # Remove 'priority-' prefix
                    break
            
            # Calculate indentation based on tree depth
            indent = ""
            if priority and priority != 'none':
                depth = priority.count('.')
                indent = "  " * depth + "- " if depth > 0 else "- "
            
            return {
                "number": issue.number,
                "title": issue.title,
                "priority": priority or "none",
                "formatted_title": f"{indent}{issue.title}" if indent else issue.title
            }
        
        return {
            "repo": repo, 
            "kanban": {
                "backlog": [format_issue_with_priority(issue) for issue in kanban.backlog],
                "plan": [format_issue_with_priority(issue) for issue in kanban.plan],
                "build": [format_issue_with_priority(issue) for issue in kanban.build],
                "measure": [format_issue_with_priority(issue) for issue in kanban.measure],
                "learn": [format_issue_with_priority(issue) for issue in kanban.learn],
                "blocked": [format_issue_with_priority(issue) for issue in kanban.blocked],
                "archived_count": len(kanban.archived)
            }
        }
    
    def get_kanban_lane(self, status: str, repo: str = None) -> dict:
        """Get issues in specific kanban lane"""
        repo = repo or self.default_repo
        issues = view_lane(repo, status)
        # Convert Issue objects to serializable dictionaries
        serializable_issues = [{"number": issue.number, "title": issue.title} for issue in issues]
        return {"repo": repo, "status": status, "issues": serializable_issues}
    
    def install_bml_workflows(self, target_repo: str) -> str:
        """Install BML automation workflows in target repository using direct file embedding"""
        import subprocess
        import tempfile
        import os
        import base64
        
        # Read all workflow files from github_workflows directory
        import pathlib
        workflow_files = {}
        workflows_dir = pathlib.Path(__file__).parent.parent / "github_workflows"
        
        for workflow_file in workflows_dir.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                workflow_files[workflow_file.name] = f.read()
        
        try:
            # Check if repo exists first
            check_result = subprocess.run(f'gh repo view {target_repo}', 
                                        shell=True, capture_output=True, text=True)
            if check_result.returncode != 0:
                return f"❌ Repository {target_repo} not found or no access"
            
            # Install workflows directly via GitHub API
            for filename, content in workflow_files.items():
                # Encode content
                content_b64 = base64.b64encode(content.encode()).decode()
                
                # Create workflow file
                cmd = f'gh api repos/{target_repo}/contents/.github/workflows/{filename} -f message="🤖 Install HEAVEN BML workflow: {filename}" -f content="{content_b64}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # File might exist, try updating
                    get_cmd = f'gh api repos/{target_repo}/contents/.github/workflows/{filename}'
                    get_result = subprocess.run(get_cmd, shell=True, capture_output=True, text=True)
                    if get_result.returncode == 0:
                        import json
                        file_info = json.loads(get_result.stdout)
                        sha = file_info['sha']
                        update_cmd = f'gh api repos/{target_repo}/contents/.github/workflows/{filename} -f message="🤖 Update HEAVEN BML workflow: {filename}" -f content="{content_b64}" -f sha="{sha}"'
                        subprocess.run(update_cmd, shell=True, check=True)
                    else:
                        return f"❌ Failed to install {filename}: {result.stderr}"
            
            # Create ideas directory
            ideas_content = """# Welcome to HEAVEN BML System!

This idea will be automatically converted to a GitHub issue by the BML workflows.

## What is BML?

Build-Measure-Learn project management using GitHub's native features:
- Tree notation priorities (priority-1.2.3...)
- Automated kanban workflow  
- AI agent integration
- Continuous improvement cycles

**Powered by HEAVEN BML System**
"""
            ideas_b64 = base64.b64encode(ideas_content.encode()).decode()
            subprocess.run(f'gh api repos/{target_repo}/contents/ideas/welcome-to-bml.md -f message="🤖 Create ideas directory" -f content="{ideas_b64}"', 
                         shell=True, capture_output=True)
            
            return f"✅ Successfully installed BML workflows in {target_repo} ({len(workflow_files)} files + ideas directory)"
                    
        except Exception as e:
            return f"❌ Error installing workflows: {str(e)}"
    
    def create_repo_with_type(self, repo_name: str, description: str = "", private: bool = True) -> str:
        """Create a new GitHub repository and install BML workflows"""
        import subprocess
        
        try:
            # Create repository without cloning initially to avoid permission issues
            visibility = "--private" if private else "--public"
            cmd = f'gh repo create {repo_name} {visibility} --description "{description}"'
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            
            # Install BML workflows in the new repo
            install_result = self.install_bml_workflows(repo_name)
            
            return f"✅ Created repository {repo_name} | {install_result}"
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout if hasattr(e, 'stdout') else str(e)
            return f"❌ Failed to create repository {repo_name}: {error_msg}"
        except Exception as e:
            return f"❌ Error creating repository: {str(e)}"
    
    def get_ecosystem_config(self, repo: str = None) -> dict:
        """Get current ecosystem.json configuration from a repository"""
        repo = repo or self.default_repo
        
        import subprocess
        try:
            cmd = f'gh api repos/{repo}/contents/ecosystem.json'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            
            # Handle JSON parsing with error handling
            try:
                file_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"JSON decode error in get_ecosystem_config: {e}")
                print(f"Command output: {result.stdout[:500]}...")
                return {
                    'repo': repo,
                    'config': None,
                    'sha': None,
                    'success': False,
                    'error': 'JSON parse error in API response'
                }
            
            content = base64.b64decode(file_data['content']).decode('utf-8')
            
            # Handle ecosystem.json parsing
            try:
                config = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON decode error in ecosystem.json: {e}")
                return {
                    'repo': repo,
                    'config': None,
                    'sha': None,
                    'success': False,
                    'error': 'Invalid ecosystem.json format'
                }
            
            return {
                'repo': repo,
                'config': config,
                'sha': file_data['sha'],
                'success': True
            }
        except subprocess.CalledProcessError as e:
            return {
                'repo': repo,
                'config': None,
                'sha': None,
                'success': False,
                'error': f'Repository access error: {e.stderr if e.stderr else "Unknown error"}'
            }
        except Exception as e:
            return {
                'repo': repo,
                'config': None,
                'sha': None,
                'success': False,
                'error': str(e)
            }
    
    def add_repo_to_ecosystem(self, meta_repo: str, target_repo: str, section: str) -> dict:
        """Add a repository to an ecosystem section"""
        import subprocess
        
        try:
            # Get current config
            current = self.get_ecosystem_config(meta_repo)
            if not current['success']:
                return current
            
            config = current['config']
            sha = current['sha']
            
            # Add repo to section
            if section not in config['sections']:
                config['sections'][section] = {
                    'description': f'Auto-created section for {section}',
                    'repos': [],
                    'auto_discover': True,
                    'show_stats': True
                }
            
            if target_repo not in config['sections'][section]['repos']:
                config['sections'][section]['repos'].append(target_repo)
            
            # Update config
            content = json.dumps(config, indent=2)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            cmd = f'gh api repos/{meta_repo}/contents/ecosystem.json -X PUT -f message="Add {target_repo} to {section} section" -f content="{encoded_content}" -f sha="{sha}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'meta_repo': meta_repo,
                'target_repo': target_repo,
                'section': section,
                'message': f'Successfully added {target_repo} to {section} section in {meta_repo}'
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f'GitHub API error: {e.stderr if e.stderr else "Unknown error"}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_ecosystem_repo(self, repo_name: str, ecosystem_type: str = 'ecosystem_meta') -> dict:
        """Create a new repository with ecosystem configuration - wraps create_repo_with_type"""
        import subprocess
        
        try:
            # Use existing create_repo_with_type function
            private = ecosystem_type == 'personal_meta'
            description = f'HEAVEN {ecosystem_type.replace("_", " ").title()} Repository'
            
            # Create the repo using existing function
            create_result = self.create_repo_with_type(repo_name, description, private)
            
            # Check if creation was successful
            if "❌" in create_result:
                return {
                    'success': False,
                    'error': create_result
                }
            
            # Now add ecosystem.json to the created repo
            name = repo_name.split('/')[1]
            
            if ecosystem_type == 'personal_meta':
                initial_config = {
                    'name': 'Personal Development Hub',
                    'description': 'Central coordination for all development projects',
                    'type': 'personal_meta',
                    'sections': {
                        'Active Projects': {
                            'description': 'Currently active development work',
                            'repos': [],
                            'auto_discover': True,
                            'show_stats': True,
                            'show_issues': True
                        }
                    },
                    'template': 'personal',
                    'auto_update': True,
                    'badges': {
                        'version': True,
                        'last_updated': True,
                        'issue_count': True
                    }
                }
            else:  # ecosystem_meta
                initial_config = {
                    'name': f'{name.replace("-", " ").title()} Ecosystem',
                    'description': 'AI Development Ecosystem',
                    'type': 'ecosystem_meta',
                    'sections': {
                        'Core Libraries': {
                            'description': 'Essential components',
                            'repos': [],
                            'auto_discover': True,
                            'show_stats': True
                        }
                    },
                    'template': 'ecosystem',
                    'auto_update': True,
                    'badges': {
                        'license': True,
                        'version': True,
                        'stars': True,
                        'last_updated': True
                    }
                }
            
            # Add ecosystem.json to repo (with retry for timing issues)
            import time
            content = json.dumps(initial_config, indent=2)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # Wait a moment for GitHub to fully initialize the repo
            time.sleep(2)
            
            cmd = f'gh api repos/{repo_name}/contents/ecosystem.json -X PUT -f message="Initialize ecosystem configuration" -f content="{encoded_content}"'
            
            # Try with retry in case of timing issues
            for attempt in range(3):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                    break
                except subprocess.CalledProcessError as e:
                    if attempt < 2:  # Not the last attempt
                        print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        raise e
            
            return {
                'success': True,
                'repo_name': repo_name,
                'ecosystem_type': ecosystem_type,
                'message': f'Ecosystem repository {repo_name} created successfully | {create_result}'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f'GitHub error adding ecosystem.json: {e.stderr if e.stderr else "Unknown error"}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


async def serve(default_repo: str = "sancovp/heaven-base") -> None:
    """Main MCP server function"""
    server = Server("heaven-bml")
    bml_server = BMLServer(default_repo)
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available BML tools"""
        return [
            Tool(
                name=BMLTools.LIST_ISSUES.value,
                description="List all issues with HEAVEN tree notation priorities. Tree notation uses hierarchical priorities like 1.2.3.4.5 where 1.2.3 comes before 1.2.4. This allows infinite nesting and precise ordering of priorities.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name=BMLTools.GET_ISSUE.value,
                description="Get details for a specific issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "GitHub issue ID",
                        },
                        "repo": {
                            "type": "string", 
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id"],
                },
            ),
            Tool(
                name=BMLTools.CREATE_ISSUE.value,
                description="Create a new GitHub issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Issue title",
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body/description",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["title"],
                },
            ),
            Tool(
                name=BMLTools.EDIT_ISSUE.value,
                description="Edit an existing GitHub issue's title and/or body",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "GitHub issue ID",
                        },
                        "title": {
                            "type": "string",
                            "description": "New issue title (optional)",
                        },
                        "body": {
                            "type": "string",
                            "description": "New issue body/description (optional)",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id"],
                },
            ),
            Tool(
                name=BMLTools.MOVE_ISSUE_ABOVE.value,
                description="Move issue above target issue. INTELLIGENT ALGORITHM: Preserves all relative positions and parent-child relationships while placing the issue exactly above the target. The system reorganizes priorities to maintain clean integer-based tree notation (1, 1.1, 1.2, 2, 2.1...). Numbers may change but positions and relationships are always preserved.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Issue ID to move",
                        },
                        "target_issue_id": {
                            "type": "string",
                            "description": "Target issue ID to move above",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id", "target_issue_id"],
                },
            ),
            Tool(
                name=BMLTools.MOVE_ISSUE_BELOW.value,
                description="Move issue below target issue. POSITION-PRESERVING: The algorithm maintains all existing relationships and tree structure while placing the issue exactly below the target. Priority numbers are intelligently reorganized to keep clean integers (no decimals). Focus on positions, not numbers - the system handles optimal numbering automatically.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Issue ID to move",
                        },
                        "target_issue_id": {
                            "type": "string",
                            "description": "Target issue ID to move below",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id", "target_issue_id"],
                },
            ),
            Tool(
                name=BMLTools.MOVE_ISSUE_BETWEEN.value,
                description="Move issue between two other issues. SMART POSITIONING: Places issue exactly between the specified targets while preserving all other relationships. The algorithm intelligently reorganizes the entire priority space to maintain clean structure. Think in terms of relative positioning - 'put this between those two' - not specific numbers.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Issue ID to move",
                        },
                        "above_issue_id": {
                            "type": "string",
                            "description": "Issue ID to be above",
                        },
                        "below_issue_id": {
                            "type": "string", 
                            "description": "Issue ID to be below",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id", "above_issue_id", "below_issue_id"],
                },
            ),
            Tool(
                name=BMLTools.SET_ISSUE_STATUS.value,
                description="Set issue status in Build-Measure-Learn workflow: backlog (ideas/requests) → plan (prioritized/designed) → build (in development) → measure (testing/validation) → learn (insights/analysis) → archived (completed). Also supports blocked status for any stage.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Issue ID to update",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["backlog", "plan", "build", "measure", "learn", "blocked", "archived"],
                            "description": "New status for the issue",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id", "status"],
                },
            ),
            Tool(
                name=BMLTools.SET_ISSUE_PRIORITY.value,
                description="Set HEAVEN tree notation priority for hierarchical task organization. Use priorities like '1', '1.1', '1.2.3' to create infinite nesting. Example: priority '1.1' makes it a subtask of priority '1'. Tree notation allows precise ordering: 1 > 1.1 > 1.2 > 1.2.1 > 1.2.2 > 1.3 > 2.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "Issue ID to update",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Tree notation priority (e.g., '1', '1.1', '1.2.3')",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["issue_id", "priority"],
                },
            ),
            Tool(
                name=BMLTools.VIEW_KANBAN.value,
                description="Get complete Build-Measure-Learn kanban board with tree notation priorities. Shows all lanes: backlog → plan → build → measure → learn → archived, plus blocked items. Issues sorted by HEAVEN tree notation (1 > 1.1 > 1.2 > 1.2.1).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name=BMLTools.GET_KANBAN_LANE.value,
                description="Get issues in a specific Build-Measure-Learn lane with tree notation priorities. Each lane represents a workflow stage: backlog (gathering), plan (prioritizing), build (developing), measure (testing), learn (analyzing), blocked (stuck), archived (done).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["backlog", "plan", "build", "measure", "learn", "blocked", "archived"],
                            "description": "Kanban lane/status to view",
                        },
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": ["status"],
                },
            ),
            Tool(
                name=BMLTools.INSTALL_BML_WORKFLOWS.value,
                description="Install HEAVEN BML automation workflows in any GitHub repository. Adds complete project management automation including auto-labeling, kanban workflows, and idea promotion. Makes any repo BML-ready for AI agent management.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_repo": {
                            "type": "string",
                            "description": "Target repository in format 'owner/repo'",
                        }
                    },
                    "required": ["target_repo"],
                },
            ),
            Tool(
                name=BMLTools.CREATE_REPO_WITH_TYPE.value,
                description="Create a new GitHub repository with BML workflows pre-installed. Sets up complete project management automation from day one. Perfect for starting new AI-managed projects with full BML capabilities.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name in format 'owner/repo'",
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description",
                        },
                        "private": {
                            "type": "boolean",
                            "description": "Whether to create private repository (default: true)",
                        }
                    },
                    "required": ["repo_name"],
                },
            ),
            Tool(
                name=BMLTools.GET_ECOSYSTEM_CONFIG.value,
                description="Get current ecosystem.json configuration from a repository. Shows the structured configuration including sections, repo lists, and settings for ecosystem/personal meta repositories.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": f"GitHub repository (default: {default_repo})",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name=BMLTools.ADD_REPO_TO_ECOSYSTEM.value,
                description="Add a repository to an ecosystem section. This updates the ecosystem.json configuration to include the target repository in the specified section, automatically creating the section if it doesn't exist.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "meta_repo": {
                            "type": "string",
                            "description": "Meta repository containing ecosystem.json",
                        },
                        "target_repo": {
                            "type": "string",
                            "description": "Repository to add to the ecosystem",
                        },
                        "section": {
                            "type": "string",
                            "description": "Section name (e.g., 'Core Libraries', 'Tools', 'Active Projects')",
                        }
                    },
                    "required": ["meta_repo", "target_repo", "section"],
                },
            ),
            Tool(
                name=BMLTools.CREATE_ECOSYSTEM_REPO.value,
                description="Create a new ecosystem repository with automatic configuration. Creates either a public ecosystem meta repo (for showcasing projects) or private personal meta repo (for personal coordination) with pre-configured ecosystem.json and README generation workflows.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name in format 'owner/repo'",
                        },
                        "ecosystem_type": {
                            "type": "string",
                            "enum": ["ecosystem_meta", "personal_meta"],
                            "description": "Type of ecosystem repo: ecosystem_meta (public showcase) or personal_meta (private coordination)",
                        }
                    },
                    "required": ["repo_name"],
                },
            ),
        ]
    
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for BML operations"""
        try:
            match name:
                case BMLTools.LIST_ISSUES.value:
                    result = bml_server.list_issues(arguments.get("repo"))
                
                case BMLTools.GET_ISSUE.value:
                    issue_id = arguments.get("issue_id")
                    if not issue_id:
                        raise ValueError("Missing required argument: issue_id")
                    result = bml_server.get_issue(issue_id, arguments.get("repo"))
                
                case BMLTools.CREATE_ISSUE.value:
                    title = arguments.get("title")
                    if not title:
                        raise ValueError("Missing required argument: title")
                    result = bml_server.create_issue(
                        title,
                        arguments.get("body", ""),
                        arguments.get("labels"),
                        arguments.get("repo")
                    )
                
                case BMLTools.EDIT_ISSUE.value:
                    issue_id = arguments.get("issue_id")
                    if not issue_id:
                        raise ValueError("Missing required argument: issue_id")
                    result = bml_server.edit_issue(
                        issue_id,
                        arguments.get("title"),
                        arguments.get("body"),
                        arguments.get("repo")
                    )
                
                case BMLTools.MOVE_ISSUE_ABOVE.value:
                    issue_id = arguments.get("issue_id")
                    target_issue_id = arguments.get("target_issue_id")
                    if not all([issue_id, target_issue_id]):
                        raise ValueError("Missing required arguments: issue_id, target_issue_id")
                    result = bml_server.move_issue_above(issue_id, target_issue_id, arguments.get("repo"))
                
                case BMLTools.MOVE_ISSUE_BELOW.value:
                    issue_id = arguments.get("issue_id")
                    target_issue_id = arguments.get("target_issue_id")
                    if not all([issue_id, target_issue_id]):
                        raise ValueError("Missing required arguments: issue_id, target_issue_id")
                    result = bml_server.move_issue_below(issue_id, target_issue_id, arguments.get("repo"))
                
                case BMLTools.MOVE_ISSUE_BETWEEN.value:
                    issue_id = arguments.get("issue_id")
                    above_issue_id = arguments.get("above_issue_id")
                    below_issue_id = arguments.get("below_issue_id")
                    if not all([issue_id, above_issue_id, below_issue_id]):
                        raise ValueError("Missing required arguments: issue_id, above_issue_id, below_issue_id")
                    result = bml_server.move_issue_between(
                        issue_id, above_issue_id, below_issue_id, arguments.get("repo")
                    )
                
                case BMLTools.SET_ISSUE_STATUS.value:
                    issue_id = arguments.get("issue_id")
                    status = arguments.get("status")
                    if not all([issue_id, status]):
                        raise ValueError("Missing required arguments: issue_id, status")
                    result = bml_server.set_issue_status(issue_id, status, arguments.get("repo"))
                
                case BMLTools.SET_ISSUE_PRIORITY.value:
                    issue_id = arguments.get("issue_id")
                    priority = arguments.get("priority")
                    if not all([issue_id, priority]):
                        raise ValueError("Missing required arguments: issue_id, priority")
                    result = bml_server.set_issue_priority(issue_id, priority, arguments.get("repo"))
                
                case BMLTools.VIEW_KANBAN.value:
                    result = bml_server.view_kanban(arguments.get("repo"))
                
                case BMLTools.GET_KANBAN_LANE.value:
                    status = arguments.get("status")
                    if not status:
                        raise ValueError("Missing required argument: status")
                    result = bml_server.get_kanban_lane(status, arguments.get("repo"))
                
                case BMLTools.INSTALL_BML_WORKFLOWS.value:
                    target_repo = arguments.get("target_repo")
                    if not target_repo:
                        raise ValueError("Missing required argument: target_repo")
                    result = bml_server.install_bml_workflows(target_repo)
                
                case BMLTools.CREATE_REPO_WITH_TYPE.value:
                    repo_name = arguments.get("repo_name")
                    if not repo_name:
                        raise ValueError("Missing required argument: repo_name")
                    result = bml_server.create_repo_with_type(
                        repo_name,
                        arguments.get("description", ""),
                        arguments.get("private", True)
                    )
                
                case BMLTools.GET_ECOSYSTEM_CONFIG.value:
                    result = bml_server.get_ecosystem_config(arguments.get("repo"))
                
                case BMLTools.ADD_REPO_TO_ECOSYSTEM.value:
                    meta_repo = arguments.get("meta_repo")
                    target_repo = arguments.get("target_repo")
                    section = arguments.get("section")
                    if not all([meta_repo, target_repo, section]):
                        raise ValueError("Missing required arguments: meta_repo, target_repo, section")
                    result = bml_server.add_repo_to_ecosystem(meta_repo, target_repo, section)
                
                case BMLTools.CREATE_ECOSYSTEM_REPO.value:
                    repo_name = arguments.get("repo_name")
                    if not repo_name:
                        raise ValueError("Missing required argument: repo_name")
                    result = bml_server.create_ecosystem_repo(
                        repo_name,
                        arguments.get("ecosystem_type", "ecosystem_meta")
                    )
                
                case _:
                    raise ValueError(f"Unknown tool: {name}")
            
            return [
                TextContent(type="text", text=json.dumps(result, indent=2))
            ]
        
        except Exception as e:
            raise ValueError(f"Error processing BML operation: {str(e)}")
    
    # Initialize server and run
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)