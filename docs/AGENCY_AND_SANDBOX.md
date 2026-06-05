# Agency and Sandbox: Bytebot Docker Integration

## 1. Container Isolation Strategy
To ensure 'Computer-Use Agency' operates safely, we employ a multi-layered isolation model:
- **Capability Stripping:** All default Linux capabilities are dropped (`--cap-drop ALL`), granting only the minimum necessary for the specific task.
- **Privilege Escalation Prevention:** The container is run with `--security-opt no-new-privileges` to prevent the agent from gaining root access.
- **Resource Constraints:** Strict CPU and memory limits are enforced via cgroups to prevent Denial of Service (DoS) attacks from the sandbox.

## 2. Mounted Folders and Persistence
- **/workspace (RW):** The primary working directory, mounted from a scoped host path. This allows the agent to interact with relevant project files while keeping the rest of the host filesystem hidden.
- **/tmp (tmpfs):** Mounted as a temporary filesystem in RAM. This ensures that transient files are never written to the host disk and are cleared automatically upon container restart.

## 3. Permission Model
- **Non-Root Execution:** The agent runs as a dedicated `bytebot` user (UID/GID mapped to the host runner) rather than root.
- **Filesystem Access:** Write access is restricted exclusively to the `/workspace` and `/tmp` directories.

## 4. Network Policy
- **Network Isolation:** The container resides in an isolated Docker bridge network with no default access to the host's local network.
- **Egress Filtering:** All outbound traffic is denied by default. API access to external services (e.g., LLM providers) must be explicitly routed through a controlled proxy or whitelisted via host-level firewall rules.

## 5. Security Approval Workflow (Human-in-the-loop)
- **Action Proposing:** The agent must propose a plan before executing any command that modifies the `/workspace`.
- **Review UI:** A CLI or Dashboard modal displays the command, the targeted files, and the expected outcome.
- **User Approval:** Explicit human confirmation is required for all write/delete operations.
