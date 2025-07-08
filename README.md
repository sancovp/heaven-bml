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
```bash
# Configure Claude Desktop
python -m mcp_server --default-repo "your-org/your-repo"
```

### 🔄 GitHub Workflow Automation
```bash
# Install BML workflows in your repository
python -m heaven_bml.setup_scripts.install_bml_workflows --repo your-org/your-repo
```

## Requirements

- Python 3.8+
- GitHub Personal Access Token with repo permissions
- Set `GITHUB_TOKEN` environment variable

## License

HEAVEN BML System License
- ✅ Personal and commercial use allowed
- ✅ Modification and distribution allowed
- **Required attribution**: "Powered by HEAVEN BML System"

---

**Powered by HEAVEN BML System**