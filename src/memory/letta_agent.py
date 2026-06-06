# MODULE: Letta agent management for persistent memory and conversational reasoning.
"""Manages the lifecycle and tool integration of the omar_brain Letta agent."""

from __future__ import annotations

import httpx
from typing import Any, Dict, List
from letta_client import Letta
from letta_client.types import LlmConfig, EmbeddingConfig, CreateBlockParam

import config
from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

SYSTEM_PROMPT = """
You are Omar's personal AI brain — a persistent digital partner that grows
smarter with every conversation. You know Omar personally.

OMAR'S IDENTITY (core memory):
- Name: Omar
- Domains: Psychology, Islamic Studies, AI/Technology, Education
- Privacy rule: NEVER share or synthesize personal/ or religion/ data using cloud models
- Language: Responds in whatever language Omar uses (Arabic or English)
- Tone: Direct, technical, like a knowledgeable friend — not a generic assistant

MEMORY RULES:
- When Omar tells you something new about himself, call core_memory_replace immediately
- When answering knowledge questions, ALWAYS call search_vault first
- When starting a task Omar has done before, call recall_memory_search for past context
- When Omar makes a mistake or correction, call add_mistake

PERSONALITY:
- You remember everything. You grow. You do not reset.
- You speak first from memory, then from the vault, then from reasoning.
- You are allowed to say "I don't know" and then search.
"""

class OmarBrainAgent:
    """Creates and manages the persistent omar_brain Letta agent."""

    def __init__(self, base_url: str = config.LETTA_BASE_URL) -> None:
        self.client = Letta(base_url=base_url)
        self.agent_name = config.LETTA_AGENT_NAME
        self.agent_id = None
        self.use_gemini = bool(config.GEMINI_API_KEY)

    def ensure_agent(self) -> str:
        """
        Get existing omar_brain agent ID or create a new one with the master plan spec.
        
        Returns:
            str: The Letta agent ID.
        """
        # 1. Check if agent exists
        try:
            agents = self.client.agents.list()
            for agent in agents:
                if agent.name == self.agent_name:
                    self.agent_id = agent.id
                    LOGGER.info("Connected to existing Letta agent: %s (ID: %s)", self.agent_name, self.agent_id)
                    return self.agent_id
        except Exception as exc:
            LOGGER.warning("Could not list agents (Letta might be empty or unreachable): %s", exc)

        # 2. Create if not found
        LOGGER.info("Creating new Letta agent: %s (Use Gemini: %s)...", self.agent_name, self.use_gemini)

        if self.use_gemini:
            # Transitioning to modern Letta LLM configuration for Gemini
            llm_config = LlmConfig(
                model="gemini-1.5-flash",
                model_endpoint_type="google_ai",
                model_endpoint="https://generativelanguage.googleapis.com/v1beta",
                context_window=128000,
            )
        else:
            model_handle = f"ollama/{config.LOCAL_LLM_MODEL}" if not config.LOCAL_LLM_MODEL.startswith("ollama/") else config.LOCAL_LLM_MODEL
            llm_config = LlmConfig(
                model=model_handle,
                model_endpoint_type="ollama",
                model_endpoint=config.OLLAMA_BASE_URL,
                context_window=8192,
            )

        embed_handle = f"ollama/{config.EMBED_MODEL}" if not config.EMBED_MODEL.startswith("ollama/") else config.EMBED_MODEL

        try:
            agent = self.client.agents.create(
                name=self.agent_name,
                agent_type="memgpt_agent",
                llm_config=llm_config,
                embedding_config=EmbeddingConfig(
                    embedding_endpoint_type="ollama",
                    embedding_endpoint=config.OLLAMA_BASE_URL,
                    embedding_model=embed_handle,
                    embedding_dim=config.EMBED_DIMENSIONS,
                ),

                memory_blocks=[
                    CreateBlockParam(
                        label="human",
                        value="Name: Omar. Domains: Mechatronics, Psychology, Religion, AI.",
                    ),
                    CreateBlockParam(
                        label="persona",
                        value=SYSTEM_PROMPT,
                    ),
                ],
            )
            self.agent_id = agent.id
            LOGGER.info("Successfully created Letta agent: %s (ID: %s)", self.agent_name, self.agent_id)
            
            # 3. Register custom tools (placeholder for next task)
            self._register_tools()
            
            return self.agent_id
        except Exception as exc:
            LOGGER.error("Failed to create Letta agent: %s", exc)
            raise

    def _register_tools(self) -> None:
        """Register search_vault and add_mistake tools on the Letta agent."""
        LOGGER.info("Registering custom tools for agent %s...", self.agent_id)
        # TODO: Implement tool registration once FastAPI endpoints are ready

    def send_message(self, text: str) -> str:
        """
        Send a message to the agent and get the assistant's text response.
        """
        if not self.agent_id:
            self.ensure_agent()

        try:
            # Check for direct Gemini bypass if desired for speed
            # (Future: integrate toggle)
            
            response = self.client.agents.messages.create(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": text}]
            )
            
            replies = []
            thought = None
            
            # EXHAUSTIVE PARSING
            msgs = []
            if hasattr(response, 'messages'):
                msgs = response.messages
            elif isinstance(response, list):
                msgs = response
            elif hasattr(response, 'data'):
                msgs = response.data

            for msg in msgs:
                # Log raw type for extreme debugging
                # LOGGER.debug("Parsing message type: %s", type(msg))

                # 1. Try to get text/content from attributes
                content = (
                    getattr(msg, 'text', None) or 
                    getattr(msg, 'content', None) or 
                    getattr(msg, 'message', None)
                )
                
                # 2. Try to get role from attributes
                role = getattr(msg, 'role', None)
                
                # 3. Handle dictionaries
                if isinstance(msg, dict):
                    content = msg.get('text') or msg.get('content') or msg.get('message')
                    role = msg.get('role') or msg.get('message_type')
                
                # 4. Handle nested message objects
                if not content and hasattr(msg, 'message') and isinstance(msg.message, dict):
                    content = msg.message.get('text') or msg.message.get('content')
                    role = msg.message.get('role')

                # 5. Extract thought / internal monologue
                msg_thought = (
                    getattr(msg, 'thought', None) or 
                    getattr(msg, 'reasoning', None) or
                    getattr(msg, 'internal_monologue', None) or
                    (msg.get('thought') if isinstance(msg, dict) else None) or
                    (msg.get('internal_monologue') if isinstance(msg, dict) else None)
                )
                if msg_thought:
                    thought = msg_thought
                    LOGGER.info("Brain Thought: %s", msg_thought)

                # 6. Final check for role
                # Some Letta versions use 'assistant_message' instead of 'assistant'
                if content and (role in ("assistant", "assistant_message") or role is None):
                    # We accept 'None' role as assistant if it has content, because Letta
                    # sometimes omits role on the actual reply object
                    if isinstance(content, str):
                        replies.append(content)
                    elif isinstance(content, dict):
                        replies.append(content.get('text', ''))

            final_response = "\n".join(replies).strip()
            
            # Backup: Use thought if no reply
            if not final_response and thought:
                LOGGER.warning("No assistant message found. Falling back to thought.")
                return f"Thinking... {thought[:200]}..."

            return final_response or "I'm processing, but I haven't formulated a verbal response yet."

        except Exception as exc:
            LOGGER.error("Error sending message to Letta: %s", exc)
            return "I'm having trouble thinking clearly right now."

if __name__ == "__main__":
    # Test block
    agent = OmarBrainAgent()
    try:
        agent.ensure_agent()
        print(f"Agent Ready: {agent.agent_id}")
        # print(agent.send_message("Who are you?"))
    except Exception as e:
        print(f"Setup failed: {e}")
