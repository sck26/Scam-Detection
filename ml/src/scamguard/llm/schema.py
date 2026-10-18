"""Validated, product-facing detection output."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from scamguard.taxonomy import DangerLevel, ScamCategory, TacticName

ShortReason = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=160),
]


class DetectionOutput(BaseModel):
    """One structured risk assessment returned by a detector."""

    model_config = ConfigDict(extra="forbid")

    danger_level: DangerLevel
    score: float = Field(ge=0.0, le=1.0)
    tactics: list[TacticName] = Field(default_factory=list, max_length=10)
    scam_category: ScamCategory
    red_flags: list[ShortReason] = Field(default_factory=list, max_length=8)
    recommended_action: ShortReason
    legit_signals: list[ShortReason] = Field(default_factory=list, max_length=8)
