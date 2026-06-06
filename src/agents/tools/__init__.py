# MODULE: Tool registry and base interface for agent capabilities.
"""Standard interface for tools used by the Task Planner and Sub-Agents."""

from __future__ import annotations

import abc
import json
from typing import Any, Dict, List, Type, Callable

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

class BaseTool(abc.ABC):
    """Abstract base class for all agent tools."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The tool's unique identifier."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Detailed description of what the tool does and its parameters."""
        pass

    @abc.abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the tool logic."""
        pass

    def to_dict(self) -> Dict[str, str]:
        """Format the tool for inclusion in an LLM system prompt."""
        return {
            "name": self.name,
            "description": self.description
        }

class ToolRegistry:
    """Discovery and management service for agent tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Add a tool to the registry."""
        self._tools[tool.name] = tool
        LOGGER.debug("Registered tool: %s", tool.name)

    def get_tool(self, name: str) -> BaseTool | None:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def get_prompt_specification(self) -> str:
        """Generate a text summary of all tools for LLM prompts."""
        specs = []
        for tool in self.list_tools():
            specs.append(f"- {tool.name}: {tool.description}")
        return "\n".join(specs)

# Global registry instance
registry = ToolRegistry()

# --- TOOL DEFINITIONS ---

class SearchVaultTool(BaseTool):
    name = "search_vault"
    description = "Search Omar's personal knowledge vault for relevant information. Args: q (str), domain (optional str)"
    
    def run(self, q: str, domain: str = None) -> Any:
        import httpx
        try:
            resp = httpx.get("http://localhost:8001/search", params={"q": q, "domain": domain, "top_k": 3})
            resp.raise_for_status()
            results = resp.json()["results"]
            if not results: return "No results found."
            return "\n\n".join([f"[{r['source_file']}] {r['text']}" for r in results])
        except Exception as e:
            return f"Search failed: {e}"

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read a file from the vault. Args: path (str)"
    
    def run(self, path: str) -> str:
        from pathlib import Path
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Failed to read file: {e}"

class SendNotificationTool(BaseTool):
    name = "send_notification"
    description = "Send a desktop notification to Omar. Args: message (str)"
    
    def run(self, message: str) -> str:
        import subprocess
        try:
            subprocess.run(["notify-send", "AI Brain", message], check=True)
            return "Notification sent."
        except Exception as e:
            return f"Failed to send notification: {e}"

class DelegateTaskTool(BaseTool):
    name = "delegate_task"
    description = "Delegate a complex task to a specialized sub-agent. Args: task (str), context (dict)"
    
    def run(self, task: str, context: dict) -> str:
        from src.agents.sub_agent import SubAgent
        try:
            agent = SubAgent(task=task, context=context)
            return agent.run()
        except Exception as e:
            return f"Delegation failed: {e}"

class PythonSandboxTool(BaseTool):
    name = "run_python"
    description = "Execute Python code in a secure sandbox. Args: code (str)"
    
    def run(self, code: str) -> str:
        from src.agents.tools.sandbox_runner import run_task_in_bytebot
        task = f"Run this python code and return the output:\n{code}"
        return run_task_in_bytebot(task)

class BrowserTool(BaseTool):
    name = "browse_url"
    description = "Browse a website and perform actions. Args: url (str), action (optional str)"
    
    def run(self, url: str, action: str = "read") -> str:
        from src.agents.tools.browser import browse_url
        return browse_url(url, action)

class ExecuteCommandTool(BaseTool):
    name = "execute_command"
    description = "Execute a local shell command on the host PC (e.g., open apps, manage files). Args: command (str)"
    
    def run(self, command: str) -> str:
        import subprocess
        try:
            # We run it detached if it's likely a GUI app to not block the brain
            is_gui = any(app in command.lower() for app in ["telegram", "firefox", "chrome", "code", "nautilus"])
            
            if is_gui:
                subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Successfully launched: {command}"
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return result.stdout.strip() or "Command executed successfully (no output)."
                else:
                    return f"Command failed (Code {result.returncode}): {result.stderr.strip()}"
        except Exception as e:
            return f"Error executing command: {e}"

# Register basic tools
registry.register(SearchVaultTool())
registry.register(ReadFileTool())
registry.register(SendNotificationTool())
registry.register(DelegateTaskTool())
registry.register(PythonSandboxTool())
registry.register(BrowserTool())
registry.register(ExecuteCommandTool())
