# MODULE: Pydantic models for the Omar core profile and memory structures.
"""Structured schema objects for core memory and the default Omar profile."""

from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel, Field


class PsychologyDomain(BaseModel):
    """Schema for psychological interests and focus areas."""

    topics: List[str] = Field(default_factory=list, description="Psychological topics of interest.")
    focus_areas: List[str] = Field(default_factory=list, description="Primary areas of focus.")


class ReligionDomain(BaseModel):
    """Schema for religious and spiritual interests."""

    traditions: List[str] = Field(default_factory=list, description="Religious traditions and lineages.")
    philosophies: List[str] = Field(default_factory=list, description="Theological or spiritual philosophies.")


class AIDomain(BaseModel):
    """Schema for AI and technical interests."""

    technologies: List[str] = Field(default_factory=list, description="AI frameworks and tools.")
    research_areas: List[str] = Field(default_factory=list, description="AI research domains.")


class OmarProfile(BaseModel):
    """Core profile schema for the user 'Omar'."""

    name: str = Field("Omar", description="The user's name.")
    psychology: PsychologyDomain = Field(default_factory=PsychologyDomain)
    religion: ReligionDomain = Field(default_factory=ReligionDomain)
    ai: AIDomain = Field(default_factory=AIDomain)
    metadata: Optional[str] = Field(None, description="Additional context or notes.")


class CoreMemorySchema(BaseModel):
    """Root object for core memory storage."""

    profile: OmarProfile
    version: str = Field("1.0.0", description="Schema version.")
