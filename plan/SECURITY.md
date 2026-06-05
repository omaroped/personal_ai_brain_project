# Security Policy: Personal AI Brain

## 1. Secret Handling Rules

### 1.1 Environment Variables
- All secrets (API keys, database credentials) MUST be stored in a `.env` file in the project root.
- The `.env` file is excluded from version control via `.gitignore`.
- Use `python-dotenv` to load secrets into the environment.

### 1.2 Credential Exposure
- Never hardcode secrets in source code, documentation, or logs.
- When logging, ensure that sensitive strings are redacted or not captured.
- Do not commit `.env` or any file containing raw secrets.

### 1.3 Local-Only Processing
- For domains tagged as `personal` or `religion`, processing MUST be restricted to local models (Ollama, Whisper, etc.).
- This is enforced by `src/api/privacy_router.py`. Bypassing this router for sensitive data is a security violation.

## 2. File Access Policy

### 2.1 Principle of Least Privilege
- The AI system should only have read access to the specific folders it monitors (`Documents`, `Downloads`, `data/vault`).
- Write access should be restricted to the `data/` directory and its subfolders.

### 2.2 Sandbox Execution
- All speculative script execution or web browsing performed by agents MUST occur inside a `Bytebot` Docker sandbox.
- The sandbox must not have direct access to the host's `.env` file or the `personal/` knowledge table.

### 2.3 User Checkpoint Gate
- Any operation that writes to the filesystem outside of the `data/` directory or modifies existing data MUST require explicit user confirmation.

## 3. Action Confirmation Policy

### 3.1 Critical Actions
The following actions require a "Y/N" confirmation in the CLI:
- Modifying `config.py` or `CLAUDE.md`.
- Deleting or overwriting files in `data/vault`.
- Exporting data to external services.
- Installing new system-level dependencies.

### 3.2 Audit Log
- All automated file modifications should be logged in a dedicated audit log within `data/logs/audit.log` (planned).

## 4. Security Audit Routine
- Periodic review of `ERRORS.md` for potential security-related failures (e.g., routing bypasses).
- Verification that `docker-compose.yml` does not expose sensitive ports to the public internet.
