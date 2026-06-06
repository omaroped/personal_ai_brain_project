# MODULE: Web browsing tool powered by Bytebot sandbox.
"""Browser tool wrapper for the agent to navigate the web securely."""

from __future__ import annotations

from src.agents.tools.sandbox_runner import run_task_in_bytebot

def browse_url(url: str, action: str = "read") -> str:
    """Navigate to a URL and return page content or perform an action.
    
    Parameters:
        url: The website to visit.
        action: What to do (e.g. 'read', 'summarize', 'find prices').
    """
    task = f"Navigate to {url} and {action}. Return the text content or a summary."
    return run_task_in_bytebot(task)

if __name__ == "__main__":
    print(browse_url("https://news.ycombinator.com", "list the top 3 stories"))
