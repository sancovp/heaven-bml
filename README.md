# HEAVEN BML System

Build-Measure-Learn GitHub project management for AI agents.

## Installation

```bash
pip install heaven-bml
```

## Quick Start

```python
# Import BML functions
from heaven_bml import (
    construct_kanban_from_labels,
    get_all_prioritized_issues,
    move_issue_above,
    move_issue_below,
    create_github_issue_with_status
)

# View your kanban board
kanban = construct_kanban_from_labels('your-org/your-repo')
print(f"Backlog: {len(kanban.backlog)} items")
print(f"Plan: {len(kanban.plan)} items")
print(f"Build: {len(kanban.build)} items")

# Create a new issue with BML status
create_github_issue_with_status(
    'your-org/your-repo',
    'Implement feature X',
    'Details about the feature',
    'plan'
)

# Manage priorities with tree notation
move_issue_above('123', '456', 'your-org/your-repo')
```

## Features

### 🌳 Tree Notation Priorities
- **Infinite hierarchy**: priority-1.2.3.4.5...
- **Automatic sorting**: Natural tree order in kanban
- **Dynamic reordering**: Move issues above/below/between

### 📋 GitHub Kanban States
- **Backlog** → **Plan** → **Build** → **Measure** → **Learn** → **Archived**
- **Label-based**: Uses GitHub labels for state management
- **API integration**: Real-time GitHub synchronization

### 🤖 MCP Server for Claude Code

**Prerequisites:** Install GitHub CLI and authenticate before configuring Claude Desktop.

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "heaven-bml": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["-m", "mcp_server", "--default-repo", "your-org/your-repo"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**Important Notes:**
- Use full Python path (adjust for your system)
- Requires Python 3.10+ for MCP server functionality
- GitHub CLI must be installed and authenticated
- GITHUB_TOKEN should have repo permissions

Then restart Claude Desktop and the BML tools will be available in Claude Code!

### 🔄 GitHub Workflow Automation
```bash
# Install BML workflows in your repository
python -m heaven_bml.setup_scripts.install_bml_workflows --repo your-org/your-repo
```

## Requirements

- Python 3.10+ (required for MCP server)
- GitHub CLI (`gh` command) installed and authenticated
- GitHub Personal Access Token with repo permissions
- Set `GITHUB_TOKEN` environment variable

### Setup Instructions

1. **Install GitHub CLI:**
   ```bash
   # macOS
   brew install gh
   
   # Windows
   winget install --id GitHub.cli
   
   # Linux
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **Authenticate GitHub CLI:**
   ```bash
   gh auth login
   # Follow prompts to authenticate with your GitHub account
   ```

3. **Verify setup:**
   ```bash
   gh auth status
   python -c "from heaven_bml import construct_kanban_from_labels; print('✅ BML functions ready')"
   ```

## License

HEAVEN BML System License
- ✅ Personal and commercial use allowed
- ✅ Modification and distribution allowed
- **Required attribution**: "Powered by HEAVEN BML System"

---

**Powered by HEAVEN BML System**