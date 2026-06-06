# MODULE: Terminal CLI for chatting with the omar_brain Letta agent.
"""Interactive CLI to test the Letta memory engine."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.memory.core_memory import LettaRuntime, CoreMemoryManager

def main():
    print("\n==============================================")
    print("🧠 Personal AI Brain - Text Memory Chat CLI 🧠")
    print("==============================================\n")
    
    # 1. Initialize Letta client
    runtime = LettaRuntime()
    print("Connecting to Letta server at http://localhost:8283...")
    try:
        agent = runtime.ensure_agent()
        agent_id = agent.get("id") or agent.get("agent_id")
        print(f"✅ Connected to agent: {agent.get('name')} (ID: {agent_id})")
    except Exception as exc:
        print(f"❌ Letta is not responding: {exc}")
        print("Please verify the Letta docker container is running.")
        sys.exit(1)

    # 2. Sync local memory
    print("\nSyncing local memory to Letta...")
    try:
        # Load local memory json
        local_mem_path = Path("data/core_memory.json")
        manager = CoreMemoryManager(memory_path=local_mem_path)
        manager.sync_to_letta()
        print("✅ Core memory synced from data/core_memory.json.")
    except Exception as exc:
        print(f"⚠️ Memory sync warning: {exc}")

    # 3. Chat loop
    print("\n💬 You can now chat with your Brain. Type 'exit' to quit.")
    print("-" * 50)
    while True:
        try:
            user_msg = input("\nYou: ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in {"exit", "quit"}:
                break
                
            # Send message to Letta agent
            # Route: POST /v1/agents/{agent_id}/messages
            url = f"http://localhost:8283/v1/agents/{agent_id}/messages"
            
            # The standard Letta request body payload uses "messages" list with "content"
            # Or "input" as syntactic sugar
            payload = {
                "input": user_msg
            }
            
            resp = httpx.post(url, json=payload, timeout=60.0)
            if resp.status_code == 422 or resp.status_code == 400:
                # Fallback to standard messages format if needed
                alt_payload = {
                    "messages": [{"role": "user", "content": user_msg}]
                }
                resp = httpx.post(url, json=alt_payload, timeout=60.0)

            resp.raise_for_status()
            response_data = resp.json()
            
            messages = response_data.get("messages", response_data)
            if isinstance(messages, list):
                for msg in messages:
                    role = msg.get("role") or msg.get("message_type")
                    text = msg.get("text") or msg.get("content")
                    # Letta thought/reasoning log if available
                    thought = msg.get("thought") or msg.get("reasoning")
                    if thought:
                        print(f"\n🧠 Thought: {thought}")
                    if (role == "assistant" or role == "assistant_message") and text:
                        print(f"\nBrain: {text}")
            else:
                print(f"\nResponse: {response_data}")
                
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"\n❌ Error during conversation: {exc}")

    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
