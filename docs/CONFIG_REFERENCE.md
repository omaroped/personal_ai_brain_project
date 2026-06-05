# Configuration Reference: Personal AI Brain

This document describes the configuration constants defined in `config.py`. These values control the behavior, paths, and model selections for the entire project.

## Directory Paths
| Constant | Description |
|---|---|
| `PROJECT_ROOT` | The absolute path to the project's root directory. |
| `DATA_DIR` | Base directory for all persistent data (Vault, VectorDB, Logs). |
| `VAULT_DIR` | Directory where raw documents are stored before ingestion. |
| `VECTORDB_DIR` | Directory containing LanceDB vector databases. |
| `LOGS_DIR` | Directory where system and error logs are kept. |
| `DOCKER_DIR` | Directory containing Docker Compose and configuration files. |
| `TESTS_DIR` | Directory containing the project's test suite. |

## Monitored Directories
| Constant | Description |
|---|---|
| `WATCH_DIRS` | A list of paths that the system monitors for new files to ingest automatically. Default includes Documents, Downloads, and the internal Vault. |

## Database & Log Files
| Constant | Description |
|---|---|
| `INGESTION_INDEX_DB` | Path to the SQLite database tracking ingestion status of files. |
| `LOG_FILE` | Path to the main application log file (`brain.log`). |

## LanceDB Collections
| Constant | Description |
|---|---|
| `LANCEDB_DOCUMENTS` | Path to the collection for general processed documents. |
| `LANCEDB_PERSONAL` | Path to the collection for personal/private data. |
| `LANCEDB_CONVERSATIONS` | Path to the collection for chat history and memory. |
| `LANCEDB_ERRORS` | Path to the collection for tracking ingestion or processing failures. |

## Network & API Settings
| Constant | Description | Env Variable | Default |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Base URL for the local Ollama API. | `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `LETTA_BASE_URL` | Base URL for the Letta agent server. | `LETTA_BASE_URL` | `http://localhost:8283` |
| `FASTAPI_HOST` | Host address for the project's API server. | `FASTAPI_HOST` | `127.0.0.1` |
| `FASTAPI_PORT` | Port for the project's API server. | `FASTAPI_PORT` | `8001` |

## Model Configuration
| Constant | Description | Env Variable | Default |
|---|---|---|---|
| `LOCAL_LLM_MODEL` | The name of the model to use via Ollama. | `LOCAL_LLM_MODEL` | `mistral` |
| `EMBED_MODEL` | The model name used for generating embeddings. | `EMBED_MODEL` | `nomic-embed-text` |
| `CLOUD_LLM_MODEL` | The cloud-based LLM used for non-sensitive tasks. | `CLOUD_LLM_MODEL` | `claude-sonnet-4-20250514` |
| `EMBED_DIMENSIONS` | The vector size of the embeddings. | - | `768` |

## Chunker Settings
| Constant | Description | Default |
|---|---|---|
| `CHUNK_SIZE_DEFAULT` | Standard number of tokens per chunk. | `512` |
| `CHUNK_OVERLAP_DEFAULT` | Standard overlap between chunks. | `80` |
| `CHUNK_SIZE_RELIGIOUS` | Smaller chunk size for dense religious texts. | `256` |
| `CHUNK_OVERLAP_RELIGIOUS` | Overlap for religious texts. | `64` |
| `CHUNK_SIZE_LECTURE` | Larger chunk size for lecture transcripts. | `600` |
| `CHUNK_OVERLAP_LECTURE` | Overlap for lecture materials. | `60` |

## Privacy & Security
| Constant | Description | Env Variable | Default |
|---|---|---|---|
| `CLOUD_BLOCKED_DOMAINS` | Categories of data that are never sent to cloud models. | - | `{"personal", "religion"}` |
| `LETTA_AGENT_NAME` | The default agent identity in Letta. | - | `omar_brain` |
| `LETTA_SERVER_PASSWORD` | Password for authenticating with Letta. | `LETTA_SERVER_PASSWORD` | `""` |
| `ANTHROPIC_API_KEY` | API Key for Claude models. | `ANTHROPIC_API_KEY` | `""` |
| `ENABLE_CLOUD_MODELS` | Global switch to allow/disallow cloud LLM usage. | `ENABLE_CLOUD_MODELS` | `false` |

## System Settings
| Constant | Description | Env Variable | Default |
|---|---|---|---|
| `LOG_LEVEL` | Verbosity of the logs (DEBUG, INFO, WARNING, ERROR). | `LOG_LEVEL` | `INFO` |
