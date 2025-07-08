"""
HEAVEN BML System - Python Functions
Universal Build-Measure-Learn project management for AI agents
"""

from .github_kanban import (
    construct_kanban_from_labels,
    view_lane,
    move_issue_to_next_status,
    move_issue_to_blocked,
    create_github_issue_with_status,
    agent_create_issue_from_idea,
    print_kanban_board
)

from .tree_kanban import (
    construct_tree_kanban,
    set_issue_tree_priority_with_inheritance,
    create_priority_label_if_needed,
    print_tree_kanban_board,
    parse_tree_priority,
    get_issue_priority_string
)

from .agent_wrappers import (
    BMLAgentWrapper,
    wrap_agent_for_bml,
    create_bml_task,
    update_task_status
)

__version__ = "1.0.0"
__author__ = "HEAVEN Development Team"
__license__ = "HEAVEN BML System License"

# Attribution requirement
ATTRIBUTION = "Powered by HEAVEN BML System"

def get_attribution():
    """Get required attribution text"""
    return ATTRIBUTION

__all__ = [
    # GitHub Kanban
    'construct_kanban_from_labels',
    'view_lane', 
    'move_issue_to_next_status',
    'move_issue_to_blocked',
    'create_github_issue_with_status',
    'agent_create_issue_from_idea',
    'print_kanban_board',
    
    # Tree Kanban
    'construct_tree_kanban',
    'set_issue_tree_priority_with_inheritance', 
    'create_priority_label_if_needed',
    'print_tree_kanban_board',
    'parse_tree_priority',
    'get_issue_priority_string',
    
    # Agent Wrappers
    'BMLAgentWrapper',
    'wrap_agent_for_bml',
    'create_bml_task', 
    'update_task_status',
    
    # Utilities
    'get_attribution'
]
