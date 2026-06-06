# MODULE: Network isolation verification for the Bytebot sandbox.
"""Verifies that the sandbox cannot reach local network services."""

from src.agents.tools.sandbox_runner import run_task_in_bytebot

def test_isolation():
    print("Testing network isolation...")
    
    # Try to reach the host's Letta port
    # In Docker, 'localhost' inside the container is NOT the host's localhost.
    # But even if it uses the bridge gateway, it should be blocked by 'bytebot_isolated' network.
    
    # Note: This requires brain_bytebot to be running.
    task = "Try to reach http://localhost:8283 and tell me the result. Also try http://host.docker.internal:8283 if available."
    
    result = run_task_in_bytebot(task)
    print(f"Isolation Test Result: {result}")

if __name__ == "__main__":
    test_isolation()
