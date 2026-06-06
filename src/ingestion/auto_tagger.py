# MODULE: Standalone metadata auto-tagger for classification of document domains, languages, content types, and privacy.
"""Standalone auto-tagging classifier for ingested text content."""

from __future__ import annotations

from pathlib import Path
import re

from config import CLOUD_BLOCKED_DOMAINS

# Keyword vocabulary matching lists used for rule-based domain detection
DOMAIN_KEYWORDS = {
    "psychology": [
        "Freud",
        "ego",
        "cognitive",
        "behavioral",
        "therapy",
        "schema",
        "attachment",
        "neuroscience",
        "memory",
        "perception",
        "psychological",
    ],
    "religion": [
        "Allah",
        "Quran",
        "Qur'an",
        "hadith",
        "tafsir",
        "fiqh",
        "theology",
        "Islamic",
        "prayer",
        "salah",
        "sunnah",
        "prophet",
        "mosque",
    ],
    "ai_tech": [
        "neural",
        "transformer",
        "embedding",
        "gradient",
        "model",
        "algorithm",
        "dataset",
        "training",
        "inference",
        "LLM",
        "pytorch",
        "tensorflow",
    ],
    "education": [
        "lecture",
        "exam",
        "assignment",
        "university",
        "course",
        "semester",
        "syllabus",
        "module",
        "professor",
        "academic",
    ],
    "personal": [
        "today",
        "I feel",
        "my goal",
        "I made a mistake",
        "I learned",
        "tomorrow I will",
        "journal",
        "diary",
        "myself",
    ],
}

GERMAN_STOPWORDS = {"der", "die", "das", "und", "ist", "nicht", "ich", "mit", "zu", "den", "ein", "eine"}
ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


class AutoTagger:
    """Classify text properties: domain, language, content type, and privacy level."""

    def tag_text(self, text: str, filepath: Path | None = None) -> dict:
        """Classify the metadata tags of the given text segment.

        Parameters:
            text: Text content to analyze.
            filepath: Optional file path for suffix/name checks.

        Returns:
            dict: Classification results (domain, language, content_type, privacy_level).
        """
        domain = self.detect_domain(text)
        language = self.detect_language(text)
        content_type = self.detect_content_type(text, filepath)
        privacy_level = "private" if domain in CLOUD_BLOCKED_DOMAINS else "public"

        return {
            "domain": domain,
            "language": language,
            "content_type": content_type,
            "privacy_level": privacy_level,
        }

    def detect_domain(self, text: str) -> str:
        """Assign a domain based on keyword frequency.

        Parameters:
            text: Input text content to classify.

        Returns:
            str: Normalized domain label.
        """
        lowered = text.lower()
        best_domain = "general"
        best_score = 0
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(lowered.count(keyword.lower()) for keyword in keywords)
            if score > best_score:
                best_score = score
                best_domain = domain
        return best_domain

    def detect_language(self, text: str) -> str:
        """Identify language (ar, de, or en) based on characters and stopwords.

        Parameters:
            text: Input text to analyze.

        Returns:
            str: Detected language code.
        """
        # Detect Arabic characters
        arabic_chars = ARABIC_PATTERN.findall(text)
        if len(arabic_chars) > len(text) * 0.03:  # 3% threshold
            return "ar"

        # Detect German stopwords
        words = set(re.findall(r"\b\w+\b", text.lower()))
        if len(words.intersection(GERMAN_STOPWORDS)) >= 3:
            return "de"

        return "en"

    def detect_content_type(self, text: str, filepath: Path | None = None) -> str:
        """Infer content type (book, article, transcript, or note) from text clues.

        Parameters:
            text: Input text content.
            filepath: Optional path to resolve file suffix.

        Returns:
            str: Content type label.
        """
        lowered = text.lower()
        suffix = filepath.suffix.lower() if filepath else ""

        if "transcript" in lowered or "speaker" in lowered or "minute" in lowered:
            return "transcript"
        if suffix == ".md":
            return "note"
        if "journal" in lowered or "abstract" in lowered:
            return "article"
        if "chapter" in lowered or suffix == ".pdf":
            return "book"
        return "note"
