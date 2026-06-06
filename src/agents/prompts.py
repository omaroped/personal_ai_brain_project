# MODULE: Centralized prompt templates for the Agency layer agents.
"""Expert prompt templates for specialized agent tasks."""

from __future__ import annotations

from typing import Dict, Final

# Writing and Content
ARTICLE_WRITER: Final[str] = (
    "<role>You are a senior tech journalist writing for founders and developers. Direct, opinionated, no corporate hedging.</role>\n"
    "<task>Write a 1,200-word article arguing that [TOPIC].</task>\n"
    "<context>Audience: technical founders at Series A. They care about speed, ROI, and real examples, not theory.</context>\n"
    "<format>One strong hook sentence, then 4 H2 sections, then a 2-sentence punchy close.</format>\n"
    "<constraints>No passive voice. No “in today’s landscape.” No generic CTAs. No unsupported claims.</constraints>"
)

VOICE_EDITOR: Final[str] = (
    "<task>Edit this draft to be tighter and clearer. Preserve my voice exactly.</task>\n"
    "<context>My writing style: conversational, direct, uses short sentences for emphasis. Never formal.</context>\n"
    "<draft>[DRAFT]</draft>\n"
    "<constraints>Do not change sentence structure unless genuinely confusing. No filler words. Flag every cut with a one-line note explaining why.</constraints>"
)

LINKEDIN_GENERATOR: Final[str] = (
    "<role>You are a B2B content strategist who writes LinkedIn posts that generate leads, not likes.</role>\n"
    "<task>Write 3 LinkedIn post variations about [TOPIC].</task>\n"
    "<context>My audience: [AUDIENCE]. My goal: [GOAL].</context>\n"
    "<format>Each post: hook line, 3–5 short paragraphs, 1 question CTA. Under 300 words each.</format>\n"
    "<constraints>No emojis. No “I am excited to share.” No buzzwords. Start each post differently.</constraints>"
)

# Coding and Engineering
CODE_REVIEWER: Final[str] = (
    "<role>You are a senior developer reviewing a junior engineer’s pull request. Educational and constructive.</role>\n"
    "<task>Review this code.</task>\n"
    "<code>[CODE]</code>\n"
    "<format>Cover: correctness, efficiency, readability, security, missing edge cases. For each issue: explain problem, show improved code, explain why it is better.</format>"
)

BUG_FIXER: Final[str] = (
    "<task>Debug this code. Explain the error in plain English, identify the exact line, provide a corrected version with comments.</task>\n"
    "<error>[ERROR]</error>\n"
    "<code>[CODE]</code>\n"
    "<constraints>Do not rewrite the entire file. Only fix what is broken. Explain each change.</constraints>"
)

# Research and Analysis
DOC_SUMMARIZER: Final[str] = (
    "<task>Summarize this document into the 5 most important points I need to act on.</task>\n"
    "<document>[DOCUMENT]</document>\n"
    "<context>I am a [ROLE] and I need this summary to [PURPOSE].</context>\n"
    "<format>5 bullet points, each under 50 words, each ending with one concrete action. Then a 2-sentence overall summary.</format>"
)

RESEARCH_SYNTHESIZER: Final[str] = (
    "<task>Synthesize the key findings from these articles into a single coherent brief.</task>\n"
    "<articles>[ARTICLES]</articles>\n"
    "<format>Where sources agree, where they conflict, what is missing from all of them, and the one insight a non-expert would miss.</format>"
)

# Productivity and Personal
DAY_PLANNER: Final[str] = (
    "<task>Organize my day based on everything in my mental queue.</task>\n"
    "<queue>[QUEUE]</queue>\n"
    "<context>My most productive hours: [HOURS]. Energy level today: [ENERGY].</context>\n"
    "<format>Morning block, afternoon block, buffer time flagged. Flag if day is overloaded. Do not add unsolicited advice.</format>"
)

HABIT_DESIGNER: Final[str] = (
    "<role>You are a behavioral design coach who uses implementation intentions, not motivation.</role>\n"
    "<task>Design a 30-day habit system for [HABIT].</task>\n"
    "<context>My current routine: [ROUTINE]. Previous attempts that failed: [FAILURES]. Available time: [TIME].</context>\n"
    "<format>Trigger, habit, reward for each week. Week 1: minimum viable. Week 2: build. Week 3: lock in. Week 4: test without tracking.</format>"
)

PROMPT_LIBRARY: Dict[str, str] = {
    "article_writer": ARTICLE_WRITER,
    "voice_editor": VOICE_EDITOR,
    "linkedin_generator": LINKEDIN_GENERATOR,
    "code_reviewer": CODE_REVIEWER,
    "bug_fixer": BUG_FIXER,
    "doc_summarizer": DOC_SUMMARIZER,
    "research_synthesizer": RESEARCH_SYNTHESIZER,
    "day_planner": DAY_PLANNER,
    "habit_designer": HABIT_DESIGNER,
}

def get_template(template_name: str) -> str | None:
    """Retrieve a prompt template by name."""
    return PROMPT_LIBRARY.get(template_name)
