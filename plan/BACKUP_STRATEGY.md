# Backup and Restore Strategy

## 1. Goal
Ensure the long-term preservation of the knowledge vault, agent memory, and system state.

## 2. Data to be Preserved

| Category | Source Path | Frequency |
|---|---|---|
| Knowledge Vault | `data/vault/` | Daily |
| Vector Database | `data/vectordb/` | Weekly (full) |
| Agent Memory | Letta (PostgreSQL volumes) | Daily |
| Ingestion State | `data/ingestion.db` | Daily |
| Personal Logs | `data/logs/` | Daily |

## 3. Backup Design

### 3.1 Local Snapshots
- Use a `tar.gz` or `rsync` approach to create local snapshots in a `backups/` directory (external to the project root).
- Snapshots should be timestamped: `brain_backup_YYYYMMDD_HHMM.tar.gz`.

### 3.2 Letta Persistence
- Utilize `pg_dump` for the PostgreSQL container to export the agent's state and conversation history.
- Ensure the Docker volume is not locked during the backup process.

### 3.3 Deduplication & Rotation
- Maintain the last 7 daily backups, 4 weekly backups, and 3 monthly backups.
- Older backups should be automatically pruned to save space.

## 4. Recovery Protocol

### 4.1 Full Restore
1. Stop all project services (Watcher, Letta).
2. Wipe the existing `data/` directory.
3. Extract the latest `tar.gz` snapshot.
4. Restore the PostgreSQL database from the `pg_dump` file.
5. Restart services and run `query.py health`.

### 4.2 Selective Restore
- Allow for individual files or tables (e.g., just the `personal` vector table) to be restored from the snapshot without a full system wipe.

## 5. Implementation Roadmap (Planned Script: `src/common/backup.py`)
- **Step 1:** Implement `backup_vault()` (simple file copy).
- **Step 2:** Implement `backup_db()` (SQLite and PostgreSQL dump).
- **Step 3:** Implement `verify_backup()` (check integrity of the archive).
- **Step 4:** Integrate with a systemd timer for automated execution.
