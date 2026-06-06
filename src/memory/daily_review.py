# MODULE: Deterministic nightly review generation for persistent memory consolidation.
"""Daily review generation helpers and CLI entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

import typer

from config import LOGS_DIR
from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

app = typer.Typer(help="Generate and save a nightly review for the AI Brain.")


def _normalize_lines(values: Iterable[str]) -> list[str]:
    """Return non-empty, stripped lines while preserving order."""
    return [value.strip() for value in values if value and value.strip()]


@dataclass
class DailyReviewRunner:
    """Generate dated markdown reviews from structured local inputs."""

    logs_dir: Path = LOGS_DIR

    def run(self, review_date: date | None = None) -> Path:
        """Create a daily review file for the supplied date."""
        target_date = review_date or date.today()
        inputs = self.collect_inputs()
        content = self.summarize_day(inputs)
        return self.write_review(target_date, content)

    def collect_inputs(self) -> dict:
        """Collect deterministic local signals for the review."""
        project_root = Path(__file__).resolve().parents[2]
        status_path = project_root / "STATUS.md"
        errors_path = project_root / "ERRORS.md"
        
        # 1. Read session logs for the day
        session_data = self._read_today_sessions()

        status_snapshot = ""
        if status_path.exists():
            status_snapshot = status_path.read_text(encoding="utf-8")

        recent_errors: list[str] = []
        if errors_path.exists():
            recent_errors = _normalize_lines(errors_path.read_text(encoding="utf-8").splitlines())[-5:]

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status_snapshot": status_snapshot,
            "recent_errors": recent_errors,
            "changed_files": [],
            "learnings": session_data.get("learnings", []),
            "blockers": [],
            "mistakes": [],
            "priorities": [],
            "session_summary": session_data.get("summary", ""),
        }

    def _read_today_sessions(self) -> dict:
        """Read and summarize today's voice interactions."""
        import json
        session_file = self.logs_dir / "sessions" / f"{date.today().isoformat()}.jsonl"
        if not session_file.exists():
            return {"learnings": [], "summary": "No voice sessions recorded today."}
        
        interactions = []
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                for line in f:
                    interactions.append(json.loads(line))
        except Exception as exc:
            LOGGER.error("Failed to read session logs: %s", exc)
            return {"learnings": [], "summary": "Error reading logs."}

        # Simple extraction (can be improved with LLM)
        summary = f"Recorded {len(interactions)} voice interactions."
        return {"learnings": [f"Voice: {i['user'][:50]}..." for i in interactions[:5]], "summary": summary}

    def compress_weekly_logs(self) -> Path | None:
        """Compress JSONL session logs older than 7 days into a markdown archive."""
        import json
        from datetime import timedelta
        
        session_dir = self.logs_dir / "sessions"
        archive_dir = self.logs_dir / "archives"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        cutoff = date.today() - timedelta(days=7)
        old_logs = sorted([f for f in session_dir.glob("*.jsonl") if date.fromisoformat(f.stem) < cutoff])
        
        if not old_logs:
            return None
            
        archive_path = archive_dir / f"sessions_upto_{cutoff.isoformat()}.md"
        with open(archive_path, "w", encoding="utf-8") as out:
            out.write(f"# Voice Session Archive (Up to {cutoff})\n\n")
            for log in old_logs:
                out.write(f"## Date: {log.stem}\n")
                with open(log, "r") as f:
                    for line in f:
                        entry = json.loads(line)
                        out.write(f"- **User:** {entry['user']}\n")
                        out.write(f"  **Brain:** {entry['brain']}\n\n")
                # Remove original log after archiving
                log.unlink()
                
        LOGGER.info("Compressed %d old session logs into %s", len(old_logs), archive_path)
        return archive_path

    def summarize_day(self, inputs: dict) -> str:
        """Render the review body using stable markdown sections."""
        changed_files = _normalize_lines(inputs.get("changed_files", []))
        learnings = _normalize_lines(inputs.get("learnings", []))
        blockers = _normalize_lines(inputs.get("blockers", []))
        mistakes = _normalize_lines(inputs.get("mistakes", []))
        priorities = _normalize_lines(inputs.get("priorities", []))
        recent_errors = _normalize_lines(inputs.get("recent_errors", []))

        if not changed_files:
            changed_files = ["No tracked file changes were provided."]
        if not learnings:
            learnings = ["No explicit learning was recorded."]
        if not blockers:
            blockers = ["No unresolved blockers were captured."]
        if not mistakes:
            mistakes = ["No repeated mistakes were recorded."]
        if not priorities:
            priorities = ["Review project status and continue the first open task."]
        if recent_errors:
            blockers = blockers + [f"Recent error log note: {value}" for value in recent_errors]

        sections = [
            ("What Changed Today", changed_files),
            ("What Was Learned", learnings),
            ("Unresolved Blockers", blockers),
            ("Repeated Mistakes", mistakes),
            ("Next Priorities", priorities),
        ]

        lines = ["# Daily Review", ""]
        for heading, items in sections:
            lines.append(f"## {heading}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write_review(self, review_date: date, content: str) -> Path:
        """Write a dated markdown review and return the resulting path."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        review_path = self.logs_dir / f"{review_date.isoformat()}.md"
        review_path.write_text(content, encoding="utf-8")
        LOGGER.info("Wrote daily review to %s", review_path)
        return review_path


@app.command()
def main(review_date: str | None = None) -> None:
    """Generate a dated daily review from local state."""
    parsed_date = date.fromisoformat(review_date) if review_date else None
    path = DailyReviewRunner().run(parsed_date)
    typer.echo(str(path))

@app.command()
def compress_logs() -> None:
    """Compress session logs older than 7 days."""
    path = DailyReviewRunner().compress_weekly_logs()
    if path:
        typer.echo(f"Archive created: {path}")
    else:
        typer.echo("No logs to compress.")


if __name__ == "__main__":
    app()
