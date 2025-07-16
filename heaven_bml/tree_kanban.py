from typing import List, Optional
from .github_kanban import KanbanBoard, Issue, construct_kanban_from_labels

def parse_tree_priority(priority_str: str) -> List[int]:
    """Parse tree notation priority into list of integers for sorting"""
    if priority_str == 'high':
        return [1]
    elif priority_str == 'medium':
        return [2] 
    elif priority_str == 'low':
        return [3]
    
    try:
        return [int(part) for part in priority_str.split('.')]
    except ValueError:
        return [999]

def get_issue_priority(issue: Issue) -> List[int]:
    """Get priority from issue labels"""
    for label in issue.labels:
        if label.startswith('priority-'):
            priority_part = label[9:]
            return parse_tree_priority(priority_part)
    return [999]

def sort_issues_by_tree_priority(issues: List[Issue]) -> List[Issue]:
    """Sort issues by tree priority"""
    return sorted(issues, key=get_issue_priority)

def construct_tree_kanban(repo: str = 'sancovp/heaven-base') -> KanbanBoard:
    """Construct kanban board with tree priority sorting"""
    board = construct_kanban_from_labels(repo)
    
    # Sort all lanes by tree priority
    board.backlog = sort_issues_by_tree_priority(board.backlog)
    board.plan = sort_issues_by_tree_priority(board.plan)
    board.build = sort_issues_by_tree_priority(board.build)
    board.measure = sort_issues_by_tree_priority(board.measure)
    board.learn = sort_issues_by_tree_priority(board.learn)
    board.blocked = sort_issues_by_tree_priority(board.blocked)
    board.archived = sort_issues_by_tree_priority(board.archived)
    
    return board

def get_issue_priority_string(issue: Issue) -> Optional[str]:
    """Get priority string from issue labels"""
    for label in issue.labels:
        if label.startswith('priority-'):
            return label[9:]
    return None

def demo_tree_kanban():
    """Demo the tree kanban system"""
    board = construct_tree_kanban()
    print("🌳 TREE KANBAN BOARD")
    print("=" * 50)
    print(f"📋 PLAN ({len(board.plan)} issues)")
    for issue in board.plan:
        priority = get_issue_priority_string(issue)
        print(f"   #{issue.number}: {issue.title[:50]} (priority: {priority or 'none'})")


def create_priority_label_if_needed(repo: str, priority: str) -> bool:
    """Create priority label if it doesn't exist"""
    import subprocess
    import json
    
    label_name = f'priority-{priority}'
    
    # Check if label exists
    try:
        cmd = f'gh api repos/{repo}/labels/{label_name}'
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True  # Label exists
    except subprocess.CalledProcessError:
        pass  # Label doesn't exist, create it
    
    # Create label with tree-aware color coding
    depth = priority.count('.')
    colors = ['1f77b4', '2ca02c', 'd62728', 'ff7f0e', '9467bd', '8c564b', 'e377c2', '7f7f7f', 'bcbd22']
    color = colors[depth % len(colors)]
    
    try:
        cmd = f'gh api repos/{repo}/labels -f name="{label_name}" -f color="{color}" -f description="Tree priority {priority}"'
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create label {label_name}: {e}")
        return False

def set_issue_tree_priority(repo: str, issue_number: int, priority: str) -> bool:
    """Set tree priority on issue, creating label if needed"""
    import subprocess
    import json
    
    # Create label if needed
    if not create_priority_label_if_needed(repo, priority):
        return False
    
    # Remove existing priority labels
    try:
        cmd = f'gh issue view {issue_number} --repo {repo} --json labels'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        
        # Debug JSON parsing
        try:
            labels_data = json.loads(result.stdout)
            labels = labels_data['labels']
        except json.JSONDecodeError as e:
            # Just continue silently - GitHub CLI sometimes returns non-JSON
            labels = []
        
        for label in labels:
            if label['name'].startswith('priority-'):
                subprocess.run(f'gh issue edit {issue_number} --repo {repo} --remove-label "{label["name"]}"', shell=True)
    except Exception as e:
        # Silently continue - GitHub CLI errors are common during bulk operations
        pass
    
    # Add new priority label
    try:
        cmd = f'gh issue edit {issue_number} --repo {repo} --add-label "priority-{priority}"'
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_parent_priority(priority: str) -> str:
    """Get parent priority from tree notation (1.2.3 -> 1.2)"""
    parts = priority.split('.')
    return '.'.join(parts[:-1]) if len(parts) > 1 else None

def find_issue_by_priority(repo: str, target_priority: str):
    """Find issue with specific priority"""
    import subprocess
    import json
    
    try:
        # Search for issues with the priority label
        cmd = f'gh issue list --repo {repo} --label "priority-{target_priority}" --json number,labels --limit 1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        issues = json.loads(result.stdout)
        return issues[0]['number'] if issues else None
    except:
        return None

def get_issue_status(repo: str, issue_number: int) -> str:
    """Get current status of an issue"""
    import subprocess
    import json
    
    try:
        cmd = f'gh issue view {issue_number} --repo {repo} --json labels'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        labels = json.loads(result.stdout)['labels']
        
        for label in labels:
            if label['name'].startswith('status-'):
                return label['name'][7:]  # Remove 'status-' prefix
        return 'backlog'  # Default status
    except:
        return 'backlog'

def create_status_label_if_needed(repo: str, status: str) -> bool:
    """Create status label if it doesn't exist"""
    import subprocess
    
    label_name = f'status-{status}'
    
    # Check if label exists
    try:
        cmd = f'gh api repos/{repo}/labels/{label_name}'
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"Label {label_name} already exists")
        return True  # Label exists
    except subprocess.CalledProcessError as e:
        print(f"Label {label_name} does not exist (code {e.returncode}), creating it...")
        # Label doesn't exist, create it
    
    # Create label with status-appropriate color
    status_colors = {
        'backlog': '0366d6',    # Blue
        'plan': '0e8a16',       # Green
        'build': 'fbca04',      # Yellow
        'measure': 'd73a49',    # Red
        'learn': '6f42c1',      # Purple
        'blocked': 'e99695',    # Light red
        'archived': '586069'    # Gray
    }
    color = status_colors.get(status, '0366d6')
    
    try:
        cmd = f'gh api repos/{repo}/labels -f name="{label_name}" -f color="{color}" -f description="BML status: {status}"'
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Created label {label_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create label {label_name}")
        print(f"Command: {cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def set_issue_status(repo: str, issue_number: int, status: str) -> bool:
    """Set status label on issue"""
    import subprocess
    import json
    
    # Create status label if needed
    if not create_status_label_if_needed(repo, status):
        print(f"Error: Could not create status label for {status}")
        return False
    
    try:
        # Add the new status label
        cmd = f'gh issue edit {issue_number} --repo {repo} --add-label "status-{status}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ Added status-{status} label to issue #{issue_number}")
        
        # Try to remove old status labels (best effort)
        try:
            cmd = f'gh issue view {issue_number} --repo {repo} --json labels'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            
            # Only parse if we get valid JSON
            if result.stdout.strip().startswith('{'):
                labels_data = json.loads(result.stdout)
                labels = labels_data.get('labels', [])
                
                for label in labels:
                    if label['name'].startswith('status-') and label['name'] != f'status-{status}':
                        subprocess.run(f'gh issue edit {issue_number} --repo {repo} --remove-label "{label["name"]}"', shell=True)
                        print(f"Removed old status label: {label['name']}")
            else:
                print(f"GitHub CLI returned non-JSON: {result.stdout[:100]}...")
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up old labels: {cleanup_error}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to set status: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error in set_issue_status: {e}")
        return False

def set_issue_tree_priority_with_inheritance(repo: str, issue_number: int, priority: str) -> bool:
    """Set tree priority with automatic status inheritance from parent"""
    
    # First set the priority label
    if not set_issue_tree_priority(repo, issue_number, priority):
        return False
    
    # Check if this is a subtask (has parent)
    parent_priority = get_parent_priority(priority)
    if parent_priority:
        # Find parent issue
        parent_issue = find_issue_by_priority(repo, parent_priority)
        if parent_issue:
            # Inherit parent's status
            parent_status = get_issue_status(repo, parent_issue)
            set_issue_status(repo, issue_number, parent_status)
            print(f"Issue #{issue_number} inherited status '{parent_status}' from parent #{parent_issue}")
    
    return True

def sync_tree_statuses(repo: str, root_priority: str) -> None:
    """Sync all issues in a tree to have consistent statuses"""
    import subprocess
    import json
    
    # Get all issues with priorities starting with root_priority
    try:
        cmd = f'gh issue list --repo {repo} --json number,labels --limit 100'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        all_issues = json.loads(result.stdout)
        
        tree_issues = []
        for issue in all_issues:
            for label in issue['labels']:
                if label['name'].startswith(f'priority-{root_priority}'):
                    priority = label['name'][9:]  # Remove 'priority-' prefix
                    tree_issues.append((issue['number'], priority))
                    break
        
        # Sort by tree depth (parents first)
        tree_issues.sort(key=lambda x: x[1].count('.'))
        
        # Apply status inheritance
        for issue_num, priority in tree_issues:
            parent_priority = get_parent_priority(priority)
            if parent_priority:
                parent_issue = find_issue_by_priority(repo, parent_priority)
                if parent_issue:
                    parent_status = get_issue_status(repo, parent_issue)
                    set_issue_status(repo, issue_num, parent_status)
                    print(f"Synced #{issue_num} (priority {priority}) to status '{parent_status}'")
    
    except Exception as e:
        print(f"Error syncing tree statuses: {e}")


# Simple Priority Management - List Manipulation + Renumbering
# ===========================================================

def get_all_prioritized_issues(repo: str) -> List[dict]:
    """Get all issues with priorities, sorted by current priority."""
    import requests
    import os
    import json
    
    headers = {
        'Authorization': f'token {os.environ["GITHUB_TOKEN"]}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(f'https://api.github.com/repos/{repo}/issues?state=open&per_page=100', headers=headers)
        response.raise_for_status()
        
        # Debug JSON parsing
        try:
            issues = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text[:500]}...")  # First 500 chars
            return []
        
        prioritized_issues = []
        for issue in issues:
            priority = None
            priority_labels = []
            
            # Collect all priority labels
            for label in issue.get('labels', []):
                if label['name'].startswith('priority-'):
                    priority_labels.append(label['name'][9:])  # Remove 'priority-' prefix
            
            if priority_labels:
                # Prefer numeric format labels over old format (high, medium, low)
                numeric_priorities = [p for p in priority_labels if p.replace('.', '').isdigit()]
                if numeric_priorities:
                    priority = numeric_priorities[0]  # Take first numeric priority
                else:
                    priority = priority_labels[0]  # Fall back to first priority
            
            # Include ALL issues, even those without priorities (will get priority "none")
            prioritized_issues.append({
                'number': issue['number'],
                'title': issue['title'],
                'priority': priority or 'none',
                'priority_parsed': parse_tree_priority(priority or 'none')
            })
        
        # Sort by parsed priority
        prioritized_issues.sort(key=lambda x: x['priority_parsed'])
        return prioritized_issues
        
    except Exception as e:
        print(f"Error getting prioritized issues: {e}")
        return []

def calculate_insertion_priority(issues: List[dict], insert_position: int) -> str:
    """Calculate the optimal priority for inserting at a specific position"""
    
    if not issues:
        return "1"
    
    if insert_position <= 0:
        # Insert before first issue
        first_priority = parse_tree_priority(issues[0]['priority'])
        if first_priority[0] > 1:
            return str(first_priority[0] - 1)
        else:
            return "0.5"
    
    if insert_position >= len(issues):
        # Insert after last issue
        last_priority = parse_tree_priority(issues[-1]['priority'])
        return str(last_priority[0] + 1)
    
    # Insert between two issues
    before_issue = issues[insert_position - 1] if insert_position > 0 else None
    after_issue = issues[insert_position]
    
    if before_issue:
        before_priority = parse_tree_priority(before_issue['priority'])
        after_priority = parse_tree_priority(after_issue['priority'])
        
        # Simple case: different root numbers
        if before_priority[0] != after_priority[0]:
            return str(before_priority[0] + 1)
        
        # Handle tree notation properly
        # Convert [1,1,1] to comparable numbers
        def tree_to_comparable(priority_list):
            # Convert [1,1,1] to 1.0101 for comparison
            result = priority_list[0]
            for i, part in enumerate(priority_list[1:], 1):
                result += part / (100 ** i)
            return result
        
        before_comparable = tree_to_comparable(before_priority)
        after_comparable = tree_to_comparable(after_priority)
        
        # Find midpoint
        mid_comparable = (before_comparable + after_comparable) / 2
        
        # Simple strategy: increment the last part of the before_priority
        # So between 1.1.1 and 1.1.3, insert 1.1.2
        if len(before_priority) == len(after_priority):
            new_priority = before_priority.copy()
            new_priority[-1] += 1
            return '.'.join(map(str, new_priority))
        else:
            # Different depths, use simpler approach
            return f"{before_priority[0]}.{before_priority[1] if len(before_priority) > 1 else 1}.5"
    
    # Fallback
    return str(parse_tree_priority(after_issue['priority'])[0])

def insert_issue_at_position(moving_issue: dict, issues: List[dict], insert_position: int, repo: str):
    """Insert issue at specific position with minimal GitHub operations"""
    
    # Calculate the priority needed for this position
    new_priority = calculate_insertion_priority(issues, insert_position)
    
    # Update only the moving issue
    success = set_issue_tree_priority(repo, str(moving_issue['number']), new_priority)
    if success:
        moving_issue['new_priority'] = new_priority
        moving_issue['priority'] = new_priority
        print(f"Set issue #{moving_issue['number']} to priority {new_priority}")
    
    return new_priority

def move_issue_above(issue_id: str, target_issue_id: str, repo: str) -> str:
    """Move issue to position above target issue."""
    all_issues = get_all_prioritized_issues(repo)
    
    # Filter to only issues that actually have priorities (not "none")
    prioritized_only = [issue for issue in all_issues if issue['priority'] != 'none']
    
    # Find and remove the issue we're moving
    moving_issue = None
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(issue_id):
            moving_issue = prioritized_only.pop(i)
            break
    
    if not moving_issue:
        raise ValueError(f"Issue #{issue_id} not found or has no priority")
    
    # Find target position
    target_position = None
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(target_issue_id):
            target_position = i
            break
    
    if target_position is None:
        raise ValueError(f"Target issue #{target_issue_id} not found")
    
    # Use smart insertion - only modify the moving issue
    new_priority = insert_issue_at_position(moving_issue, prioritized_only, target_position, repo)
    
    result = f"Moved issue #{issue_id} above #{target_issue_id} | List position: {target_position + 1} | Priority: {new_priority}"
    print(result)
    return result

def move_issue_below(issue_id: str, target_issue_id: str, repo: str) -> str:
    """Move issue to position below target issue."""
    all_issues = get_all_prioritized_issues(repo)
    
    # Filter to only issues that actually have priorities (not "none")
    prioritized_only = [issue for issue in all_issues if issue['priority'] != 'none']
    
    # Find and remove the issue we're moving
    moving_issue = None
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(issue_id):
            moving_issue = prioritized_only.pop(i)
            break
    
    if not moving_issue:
        raise ValueError(f"Issue #{issue_id} not found or has no priority")
    
    # Find target position
    target_position = None
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(target_issue_id):
            target_position = i + 1  # Insert after target
            break
    
    if target_position is None:
        raise ValueError(f"Target issue #{target_issue_id} not found")
    
    # Use smart insertion - only modify the moving issue
    new_priority = insert_issue_at_position(moving_issue, prioritized_only, target_position, repo)
    
    result = f"Moved issue #{issue_id} below #{target_issue_id} | List position: {target_position + 1} | Priority: {new_priority}"
    print(result)
    return result

def move_issue_between(issue_id: str, above_issue_id: str, below_issue_id: str, repo: str) -> str:
    """Move issue between two other issues."""
    all_issues = get_all_prioritized_issues(repo)
    
    # Filter to only issues that actually have priorities (not "none")
    prioritized_only = [issue for issue in all_issues if issue['priority'] != 'none']
    
    # Find and remove the issue we're moving
    moving_issue = None
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(issue_id):
            moving_issue = prioritized_only.pop(i)
            break
    
    if not moving_issue:
        raise ValueError(f"Issue #{issue_id} not found or has no priority")
    
    # Find positions of above and below issues
    above_position = None
    below_position = None
    
    for i, issue in enumerate(prioritized_only):
        if str(issue['number']) == str(above_issue_id):
            above_position = i
        elif str(issue['number']) == str(below_issue_id):
            below_position = i
    
    if above_position is None:
        raise ValueError(f"Above issue #{above_issue_id} not found")
    if below_position is None:
        raise ValueError(f"Below issue #{below_issue_id} not found")
    
    if above_position >= below_position:
        raise ValueError(f"Above issue must have higher priority than below issue")
    
    # Insert between them (right after the above issue)
    insert_position = above_position + 1
    
    # Use smart insertion - only modify the moving issue
    new_priority = insert_issue_at_position(moving_issue, prioritized_only, insert_position, repo)
    
    result = f"Moved issue #{issue_id} between #{above_issue_id} and #{below_issue_id} | List position: {insert_position + 1} | Priority: {new_priority}"
    print(result)
    return result


def print_tree_kanban_board(repo: str) -> None:
    """Print kanban board showing: backlog count, full plan details, build status"""
    from .github_kanban import construct_kanban_from_labels, get_issue_priority, get_issue_priority_string
    
    kanban = construct_kanban_from_labels(repo)
    
    # 1. Backlog count only
    backlog_count = len(kanban.backlog)
    print(f"Backlog: {backlog_count} items")
    
    # 2. Full plan details (titles, numbers, priorities)
    plan_issues = kanban.plan
    if plan_issues:
        print(f"\nPlan ({len(plan_issues)} items):")
        sorted_plan = sorted(plan_issues, key=lambda issue: get_issue_priority(issue))
        for issue in sorted_plan:
            priority = get_issue_priority_string(issue)
            print(f"  {priority} │ #{issue.number} │ {issue.title}")
    else:
        print("\nPlan: empty")
    
    # 3. Build status issues
    build_issues = kanban.build
    if build_issues:
        print(f"\nBuild ({len(build_issues)} items):")
        sorted_build = sorted(build_issues, key=lambda issue: get_issue_priority(issue))
        for issue in sorted_build:
            priority = get_issue_priority_string(issue)
            print(f"  {priority} │ #{issue.number} │ {issue.title}")
    else:
        print("\nBuild: empty")


def sync_slot_map_to_priorities(slot_map: dict, repo: str = 'sancovp/heaven-base') -> bool:
    """
    Sync frontend slot map to GitHub priorities and status labels.
    
    Args:
        slot_map: Dictionary with lanes as keys, each containing list of 
                 {issueId: int, parentSlot: int|None} objects
        repo: GitHub repository
        
    Returns:
        bool: True if successful, False otherwise
    """
    import subprocess
    import json
    
    # BML workflow order (learn is highest priority)
    lane_order = ['learn', 'measure', 'build', 'plan', 'backlog']
    
    # Flatten all issues across lanes with their lane info
    all_issues = []
    for lane in lane_order:
        if lane in slot_map:
            for slot_index, issue_data in enumerate(slot_map[lane]):
                all_issues.append({
                    'issueId': issue_data['issueId'],
                    'parentSlot': issue_data['parentSlot'],
                    'lane': lane,
                    'slotIndex': slot_index
                })
    
    # Calculate priorities
    slot_to_priority = {}  # slotIndex -> priority string
    root_priority_counter = 1
    
    for issue in all_issues:
        global_slot_key = f"{issue['lane']}_{issue['slotIndex']}"
        
        if issue['parentSlot'] is None:
            # Top-level issue gets next sequential priority
            priority = str(root_priority_counter)
            root_priority_counter += 1
        else:
            # Child issue: find parent priority, count siblings, assign next child number
            parent_slot_key = f"{issue['lane']}_{issue['parentSlot']}"
            if parent_slot_key not in slot_to_priority:
                print(f"Error: Parent slot {parent_slot_key} not found for issue {issue['issueId']}")
                return False
                
            parent_priority = slot_to_priority[parent_slot_key]
            
            # Count existing children of this parent
            existing_children = [p for p in slot_to_priority.values() 
                               if p.startswith(f"{parent_priority}.")]
            child_number = len(existing_children) + 1
            priority = f"{parent_priority}.{child_number}"
        
        slot_to_priority[global_slot_key] = priority
    
    # Batch update all issues
    success_count = 0
    total_issues = len(all_issues)
    
    for issue in all_issues:
        global_slot_key = f"{issue['lane']}_{issue['slotIndex']}"
        priority = slot_to_priority[global_slot_key]
        
        try:
            # Update both priority and status labels in one operation
            success = update_issue_priority_and_status(
                repo, 
                issue['issueId'], 
                priority, 
                issue['lane']
            )
            
            if success:
                success_count += 1
                print(f"✅ Updated issue #{issue['issueId']}: priority={priority}, status={issue['lane']}")
            else:
                print(f"❌ Failed to update issue #{issue['issueId']}")
                
        except Exception as e:
            print(f"❌ Error updating issue #{issue['issueId']}: {e}")
    
    print(f"\nSync complete: {success_count}/{total_issues} issues updated")
    return success_count == total_issues


def update_issue_priority_and_status(repo: str, issue_number: int, priority: str, status: str) -> bool:
    """
    Update both priority and status labels for an issue in a single operation.
    """
    import subprocess
    import json
    
    # Create priority label if needed
    if not create_priority_label_if_needed(repo, priority):
        print(f"Failed to create priority label for {priority}")
        return False
    
    # Create status label if needed
    if not create_status_label_if_needed(repo, status):
        print(f"Failed to create status label for {status}")
        return False
    
    try:
        # Get current labels
        cmd = f'gh issue view {issue_number} --repo {repo} --json labels'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        
        if result.stdout.strip().startswith('{'):
            labels_data = json.loads(result.stdout)
            current_labels = labels_data.get('labels', [])
            
            # Remove old priority and status labels
            labels_to_remove = []
            for label in current_labels:
                if label['name'].startswith('priority-') or label['name'].startswith('status-'):
                    labels_to_remove.append(label['name'])
            
            # Remove old labels
            for label_name in labels_to_remove:
                subprocess.run(f'gh issue edit {issue_number} --repo {repo} --remove-label "{label_name}"', 
                             shell=True, capture_output=True)
        
        # Add new priority and status labels
        new_labels = [f'priority-{priority}', f'status-{status}']
        for label in new_labels:
            cmd = f'gh issue edit {issue_number} --repo {repo} --add-label "{label}"'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        
        return True
        
    except Exception as e:
        print(f"Error updating issue #{issue_number}: {e}")
        return False

