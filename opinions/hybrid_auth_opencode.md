# Hybrid Auth Architecture: Bypassing API Keys via OpenCode.ai

## The Problem
Mechatronics engineers and developers often have personal subscriptions to AI services (ChatGPT Plus, Gemini Advanced, Claude Pro) but do not want to manage separate developer API keys, pay for usage twice, or deal with the latency/cost of standard cloud APIs for personal projects.

## The "OpenCode" Solution
The architecture leverages **OpenCode.ai**, an open-source AI agent that supports direct user authentication (`opencode auth login`). By using OpenCode as a local proxy, the Personal AI Brain can "borrow" the user's existing authenticated sessions.

## Coexistence with Privacy
This architecture integrates with the project's **Privacy Router**. 
- **Local Route:** For `personal` or `religion` domains, use Ollama/Mistral.
- **Cloud (Auth) Route:** For general knowledge or synthesis, use OpenCode authenticated with the user's Gemini/OpenAI account.
- **Cloud (API) Route:** Fallback for high-reliability synthesis where an API key is preferred.

## Technical Implementation
1. **Bridge Layer:** A local gateway (e.g., `opencode-to-openai` or a custom Python wrapper) that translates OpenCode's CLI/Web-session capabilities into a standard OpenAI-compatible REST API.
2. **Dashboard Integration:** A "Provider Manager" UI where the user can select a model and, if using a cloud provider, trigger the `opencode auth login` flow or provide a session token.
3. **Endpoint Mapping:** Letta is configured to point its `llm_config` at `http://localhost:8083/v1` (the OpenCode gateway) instead of direct cloud APIs.

## Benefits
- **Zero Cost:** Uses existing personal quotas.
- **High Performance:** Access to GPT-4o and Gemini 1.5 Pro/Ultra.
- **Unified Identity:** The agent operates with the same "knowledge" and limits as the user's personal accounts.
- **No Secret Management:** No `.env` keys to rotate; auth is handled via browser OAuth.
