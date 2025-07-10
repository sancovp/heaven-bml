# HEAVEN BML MCP Server

Build-Measure-Learn GitHub project management for AI agents via Model Context Protocol.

## Features

- **Issue Management**: List, create, and get GitHub issues
- **Priority Management**: Move issues above/below/between other issues
- **Kanban Board**: View complete kanban board or specific lanes
- **Status Management**: Move issues between BML statuses (Backlog → Plan → Build → Measure → Learn → Blocked → Archived)

## Installation

```bash
pip install heaven-bml
```

## Usage

### With Claude Code (Recommended)

Add the MCP server to Claude Code:

```bash
claude mcp add heaven-bml -e GITHUB_TOKEN="your_github_token_here" -- python3 -m mcp_server --default-repo your-org/your-repo
```

Replace:
- `your_github_token_here` with your GitHub Personal Access Token
- `your-org/your-repo` with your default GitHub repository
- `python3` with your Python executable path if needed

### As Standalone MCP Server
```bash
python -m mcp_server --default-repo "your-org/your-repo"
```

### Available Tools

1. **list_issues** - Get all prioritized issues
2. **get_issue** - Get specific issue details  
3. **create_issue** - Create new issues
4. **move_issue_above** - Move issue above target
5. **move_issue_below** - Move issue below target
6. **move_issue_between** - Move issue between two others
7. **set_issue_status** - Change issue status
8. **view_kanban** - Get complete kanban board
9. **get_kanban_lane** - Get specific status lane

## Configuration with Claude Desktop

1. Copy `claude_desktop_config_template.json` to your Claude Desktop configuration
2. Replace `your-org/your-repo` with your GitHub repository
3. Replace `your_github_token_here` with your GitHub Personal Access Token
4. Restart Claude Desktop

The token needs these permissions:
- `repo` (for private repositories)
- `public_repo` (for public repositories) 
- `read:org` (for organization repositories)

## Current Status

✅ **FULLY FUNCTIONAL** - Real BML system with live GitHub integration

- Real heaven-bml-system package installed and working
- Live GitHub API calls retrieving actual project data
- All 9 MCP tools tested and verified
- Ready for production use with Claude Code

## Integration Test Results

- ✅ 36 total issues managed across kanban board
- ✅ Backlog: 23 items, Plan: 12 items, Build: 1 item
- ✅ All priority management functions operational
- ✅ Real-time GitHub synchronization working