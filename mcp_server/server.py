"""
BML MCP Server - Build-Measure-Learn GitHub project management for AI agents
"""
import json
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
    MOVE_ISSUE_ABOVE = "move_issue_above"
    MOVE_ISSUE_BELOW = "move_issue_below"
    MOVE_ISSUE_BETWEEN = "move_issue_between"
    SET_ISSUE_STATUS = "set_issue_status"
    SET_ISSUE_PRIORITY = "set_issue_priority"
    VIEW_KANBAN = "view_kanban"
    GET_KANBAN_LANE = "get_kanban_lane"
    INSTALL_BML_WORKFLOWS = "install_bml_workflows"
    CREATE_REPO_WITH_TYPE = "create_repo_with_type"


# Import real BML functions from heaven-bml-system package
try:
    from heaven_bml.tree_kanban import (
        get_all_prioritized_issues,
        move_issue_above,
        move_issue_below, 
        move_issue_between,
        set_issue_tree_priority
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
        """Get complete kanban board view"""
        repo = repo or self.default_repo
        kanban = construct_kanban_from_labels(repo)
        return {
            "repo": repo, 
            "kanban": {
                "backlog": [{"number": issue.number, "title": issue.title} for issue in kanban.backlog],
                "plan": [{"number": issue.number, "title": issue.title} for issue in kanban.plan],
                "build": [{"number": issue.number, "title": issue.title} for issue in kanban.build],
                "measure": [{"number": issue.number, "title": issue.title} for issue in kanban.measure],
                "learn": [{"number": issue.number, "title": issue.title} for issue in kanban.learn],
                "blocked": [{"number": issue.number, "title": issue.title} for issue in kanban.blocked],
                "archived": [{"number": issue.number, "title": issue.title} for issue in kanban.archived]
            }
        }
    
    def get_kanban_lane(self, status: str, repo: str = None) -> dict:
        """Get issues in specific kanban lane"""
        repo = repo or self.default_repo
        issues = view_lane(repo, status)
        return {"repo": repo, "status": status, "issues": issues}
    
    def install_bml_workflows(self, target_repo: str) -> str:
        """Install BML automation workflows in target repository using GitHub CLI"""
        import subprocess
        import tempfile
        import os
        
        try:
            # Import the existing install function
            from setup_scripts.install_bml_workflows import install_bml_workflows as install_local
            
            # Clone the target repo temporarily
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, "repo")
                
                # Clone the repository
                subprocess.run(f'gh repo clone {target_repo} "{clone_path}"', 
                             shell=True, check=True, capture_output=True)
                
                # Install workflows using our existing function
                success = install_local(clone_path, target_repo)
                
                if success:
                    # Commit and push changes
                    os.chdir(clone_path)
                    subprocess.run('git add .', shell=True, check=True)
                    subprocess.run('git commit -m "🤖 Install HEAVEN BML automation workflows"', 
                                 shell=True, check=True)
                    subprocess.run('git push', shell=True, check=True)
                    
                    return f"✅ Successfully installed BML workflows in {target_repo}"
                else:
                    return f"❌ Failed to install workflows in {target_repo}"
                    
        except Exception as e:
            return f"❌ Error installing workflows: {str(e)}"
    
    def create_repo_with_type(self, repo_name: str, description: str = "", private: bool = True) -> str:
        """Create a new GitHub repository and install BML workflows"""
        import subprocess
        
        try:
            # Create repository
            visibility = "--private" if private else "--public"
            cmd = f'gh repo create {repo_name} {visibility} --description "{description}" --clone'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            # Install BML workflows in the new repo
            install_result = self.install_bml_workflows(repo_name)
            
            return f"✅ Created repository {repo_name} | {install_result}"
            
        except subprocess.CalledProcessError as e:
            return f"❌ Failed to create repository {repo_name}: {e.stderr}"
        except Exception as e:
            return f"❌ Error creating repository: {str(e)}"


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