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
            "learnings": [],
            "blockers": [],
            "mistakes": [],
            "priorities": [],
        }

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


if __name__ == "__main__":
    app()
