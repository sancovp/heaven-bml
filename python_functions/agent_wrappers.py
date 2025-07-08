"""
HEAVEN BML System - Agent Framework Wrappers
Universal wrappers for any AI agent framework to use BML system
"""

from typing import Any, Dict, Optional, Callable, List
from .github_kanban import create_github_issue_with_status, move_issue_to_next_status
from .tree_kanban import set_issue_tree_priority_with_inheritance


class BMLAgentWrapper:
    """Universal wrapper for any AI agent to use BML system"""
    
    def __init__(self, repo: str, agent: Any = None, agent_execute_func: Callable = None):
        self.repo = repo
        self.agent = agent
        self.agent_execute_func = agent_execute_func or self._default_execute
        
    def _default_execute(self, task: str) -> Dict[str, Any]:
        """Default execution - override with your agent's execute method"""
        return {"status": "completed", "result": f"Executed: {task}"}
    
    def create_task(self, title: str, description: str, priority: str = None, 
                   status: str = "backlog") -> int:
        """Create a new BML task"""
        issue_num = create_github_issue_with_status(
            repo=self.repo,
            title=title,
            body=description,
            status=status,
            priority="medium"
        )
        
        if priority:
            set_issue_tree_priority_with_inheritance(self.repo, issue_num, priority)
            
        return issue_num
    
    def execute_task(self, issue_number: int, task_description: str) -> Dict[str, Any]:
        """Execute a task and update BML status"""
        # Move to build status
        move_issue_to_next_status(self.repo, issue_number, "build")
        
        try:
            # Execute with wrapped agent
            result = self.agent_execute_func(task_description)
            
            # Move to measure status on success
            move_issue_to_next_status(self.repo, issue_number, "measure")
            
            return result
            
        except Exception as e:
            # Move to blocked on failure
            from .github_kanban import move_issue_to_blocked
            move_issue_to_blocked(self.repo, issue_number, f"Execution failed: {str(e)}")
            raise
    
    def complete_task(self, issue_number: int, lessons_learned: str = None):
        """Complete a task and move to learn phase"""
        move_issue_to_next_status(self.repo, issue_number, "learn")
        
        if lessons_learned:
            # Add lessons as comment
            import subprocess
            cmd = f'gh issue comment {issue_number} --repo {self.repo} --body "📚 **Lessons Learned:**\n\n{lessons_learned}"'
            subprocess.run(cmd, shell=True)


def wrap_agent_for_bml(agent: Any, repo: str, execute_method: str = "run") -> BMLAgentWrapper:
    """Wrap any agent with BML capabilities"""
    
    def execute_func(task: str):
        if hasattr(agent, execute_method):
            return getattr(agent, execute_method)(task)
        else:
            raise AttributeError(f"Agent does not have method: {execute_method}")
    
    return BMLAgentWrapper(repo=repo, agent=agent, agent_execute_func=execute_func)


def create_bml_task(repo: str, title: str, description: str, priority: str = None) -> int:
    """Standalone function to create BML task"""
    wrapper = BMLAgentWrapper(repo)
    return wrapper.create_task(title, description, priority)


def update_task_status(repo: str, issue_number: int, new_status: str) -> bool:
    """Standalone function to update task status"""
    return move_issue_to_next_status(repo, issue_number, new_status)


# Framework-specific convenience functions

def wrap_langchain_agent(agent, repo: str) -> BMLAgentWrapper:
    """Convenience wrapper for LangChain agents"""
    return wrap_agent_for_bml(agent, repo, execute_method="run")


def wrap_crewai_agent(agent, repo: str) -> BMLAgentWrapper:
    """Convenience wrapper for CrewAI agents"""
    return wrap_agent_for_bml(agent, repo, execute_method="execute")


def wrap_autogen_agent(agent, repo: str) -> BMLAgentWrapper:
    """Convenience wrapper for AutoGen agents"""
    return wrap_agent_for_bml(agent, repo, execute_method="generate_reply")


# Example usage demonstrations
if __name__ == "__main__":
    print("HEAVEN BML System - Agent Wrappers")
    print("Universal integration for any AI agent framework")
    print()
    print("Example usage:")
    print("  wrapper = wrap_agent_for_bml(my_agent, 'owner/repo')")
    print("  task_id = wrapper.create_task('Implement feature X', 'Description...')")
    print("  result = wrapper.execute_task(task_id, 'Build the feature')")
    print("  wrapper.complete_task(task_id, 'Learned: Always validate inputs')")
