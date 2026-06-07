# Threat Model

## Scope

This threat model covers the local-first Personal AI Brain runtime with optional cloud-provider fallbacks and system-control tools.

## Primary Threats

### Prompt injection via ingested content

Risk:

- a document or web clipping attempts to manipulate planner or memory behavior

Mitigation direction:

- retrieval is separate from tool execution
- planner must not execute tool instructions found in retrieved text automatically

### Unsafe tool execution

Risk:

- agent invokes destructive or privileged actions without meaningful user approval

Mitigation direction:

- tool safety classes
- confirmation gate for destructive and local-write actions
- audit logging

### Data exfiltration through provider routing

Risk:

- sensitive domains leave the machine through cloud fallbacks

Mitigation direction:

- privacy routing
- explicit local-only domain enforcement
- tests around blocked domains

### Browser or sandbox escape assumptions

Risk:

- “sandboxed” tooling is treated as safe without proven boundaries

Mitigation direction:

- explicit isolation verification
- clear documentation of guarantees and non-guarantees

### Secret leakage

Risk:

- API keys or auth tokens leak through config, logs, or subprocess behavior

Mitigation direction:

- environment-variable based secrets
- avoid logging raw secrets
- isolate provider adapters
