# MODULE: Parser for durable updates extracted from daily review markdown files.
"""Daily review extraction into structured core memory updates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(normalized)
    return ordered


@dataclass
class DailyReviewExtractor:
    """Extract durable goals, mistakes, and domain changes from daily reviews."""

    def extract_updates(self, review_path: Path) -> dict:
        """Read a markdown review and return structured memory updates."""
        text = review_path.read_text(encoding="utf-8")
        return {
            "goals": self.detect_goals(text),
            "mistakes": self.detect_mistakes(text),
            "domains": self.detect_domain_changes(text),
            "last_reviewed_at": review_path.stem,
        }

    def detect_goals(self, text: str) -> list[str]:
        """Extract durable future-oriented priorities from review text."""
        goals: list[str] = []
        for line in text.splitlines():
            stripped = line.strip().lstrip("-").strip()
            lowered = stripped.lower()
            if lowered.startswith("next step:"):
                goals.append(stripped.split(":", 1)[1].strip())
            elif lowered.startswith("next priorities"):
                continue
            elif "priority" in lowered and ":" in stripped:
                goals.append(stripped.split(":", 1)[1].strip())
        return _dedupe_preserve_order(goals)

    def detect_mistakes(self, text: str) -> list[dict]:
        """Extract repeated mistakes with any available correction."""
        mistakes: list[dict] = []
        for line in text.splitlines():
            stripped = line.strip().lstrip("-").strip()
            lowered = stripped.lower()
            if "mistake:" in lowered or "repeated mistake:" in lowered:
                _, detail = stripped.split(":", 1)
                context, correction = self._split_correction(detail.strip())
                mistakes.append({"context": context, "correction": correction})
        unique: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for mistake in mistakes:
            key = (mistake["context"].lower(), mistake["correction"].lower())
            if key not in seen:
                seen.add(key)
                unique.append(mistake)
        return unique

    def detect_domain_changes(self, text: str) -> list[str]:
        """Extract durable domain shifts or focus areas mentioned in the review."""
        domain_keywords = {
            "psychology": ["psychology", "therapy", "cognitive", "behavioral"],
            "religion": ["religion", "tafsir", "hadith", "fiqh", "allah", "quran"],
            "ai_tech": ["ai", "embedding", "model", "vector", "runtime", "docker"],
            "education": ["course", "lecture", "study", "assignment", "university"],
            "personal": ["habit", "routine", "personal", "future self"],
        }
        lowered = text.lower()
        matches = [domain for domain, keywords in domain_keywords.items() if any(keyword in lowered for keyword in keywords)]
        return _dedupe_preserve_order(matches)

    def _split_correction(self, detail: str) -> tuple[str, str]:
        """Split a mistake line into context and correction text when possible."""
        parts = re.split(r"\b(?:learned|fix|correction)\b", detail, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            context = parts[0].strip(" -;.")
            correction = parts[1].strip(" -;:.")
            return context, correction
        return detail.strip(), ""
