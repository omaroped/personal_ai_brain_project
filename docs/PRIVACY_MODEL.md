# Privacy Model

The Personal AI Brain project is built on the principle of local-first privacy. Sensitive data is protected through hardcoded routing rules.

## Table Routing

Data is partitioned into separate tables within LanceDB based on its sensitivity:

- **Documents Table (`documents`)**: Contains general knowledge, academic papers, and technical documentation. This data is considered low-sensitivity.
- **Personal Table (`personal`)**: Contains daily logs, private notes, and religious studies. This data is considered high-sensitivity and is subject to strict routing rules.

## Privacy Routing Rules

The system implements a routing layer that inspects the "domain" of the data before it is processed by an LLM:

1. **Blocked Domains**: Any data tagged with `personal` or `religion` is strictly forbidden from being sent to cloud-based LLM providers (e.g., OpenAI, Anthropic).
2. **Local Processing**: High-sensitivity data is processed exclusively by local models running via Ollama (e.g., Mistral, Llama 3).
3. **Implicit Routing**: If a query targets the `personal` table, the system automatically defaults to local-only mode regardless of the requested task complexity.

## Domain Matrix

| Domain | Sensitivity | Model Routing |
|---|---|---|
| `personal` | High | Local Only |
| `religion` | High | Local Only |
| `psychology` | Medium | Local Preferred |
| `ai_tech` | Low | Cloud Allowed |
| `education` | Low | Cloud Allowed |
| `public` | Low | Cloud Allowed |
