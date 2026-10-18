"""Typed access to the shared ScamGuard tactic taxonomy."""

from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator
from yaml.nodes import MappingNode


class DangerLevel(StrEnum):
    """User-facing risk classifications."""

    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


class Channel(StrEnum):
    """Supported message origins."""

    SMS = "sms"
    EMAIL = "email"
    CHAT = "chat"
    SOCIAL = "social"
    OTHER = "other"


class TacticName(StrEnum):
    """Generalizable manipulation tactics used by scams."""

    URGENCY = "urgency"
    THREAT = "threat"
    IMPERSONATION = "impersonation"
    UNUSUAL_PAYMENT = "unusual_payment"
    CREDENTIAL_REQUEST = "credential_request"
    OFF_PLATFORM_PUSH = "off_platform_push"
    TOO_GOOD_TO_BE_TRUE = "too_good_to_be_true"
    SECRECY = "secrecy"
    LOOKALIKE_LINK = "lookalike_link"
    RELATIONSHIP_EXPLOIT = "relationship_exploit"


class ScamCategory(StrEnum):
    """Reporting categories; detectors should reason about tactics instead."""

    PACKAGE_DELIVERY = "package_delivery"
    BANK_ALERT = "bank_alert"
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    TECH_SUPPORT = "tech_support"
    ROMANCE = "romance"
    FAMILY_EMERGENCY = "family_emergency"
    JOB_OFFER = "job_offer"
    PRIZE_OR_LOTTERY = "prize_or_lottery"
    INVESTMENT_CRYPTO = "investment_crypto"
    MARKETPLACE = "marketplace"
    UTILITY_OR_BILLING = "utility_or_billing"
    OTHER = "other"


class TacticDefinition(BaseModel):
    """Human-readable guidance for one tactic."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    definition: str = Field(min_length=10)
    examples: tuple[str, str]


class Taxonomy(BaseModel):
    """Validated, complete taxonomy shared across product components."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    danger_levels: tuple[DangerLevel, ...]
    channels: tuple[Channel, ...]
    tactics: dict[TacticName, TacticDefinition]
    categories: tuple[ScamCategory, ...]

    @model_validator(mode="after")
    def validate_completeness(self) -> "Taxonomy":
        expected = {
            "danger_levels": set(DangerLevel),
            "channels": set(Channel),
            "tactics": set(TacticName),
            "categories": set(ScamCategory),
        }
        actual = {
            "danger_levels": set(self.danger_levels),
            "channels": set(self.channels),
            "tactics": set(self.tactics),
            "categories": set(self.categories),
        }
        for field_name, expected_values in expected.items():
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} contains duplicate values")
            if actual[field_name] != expected_values:
                message = f"{field_name} must contain every defined value exactly once"
                raise ValueError(message)
        return self


class DuplicateKeyError(ValueError):
    """Raised when a YAML mapping repeats a key."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: yaml.SafeLoader, node: MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_taxonomy(path: Path | None = None) -> Taxonomy:
    """Load and validate the bundled taxonomy or a supplied YAML file."""

    taxonomy_path = path or Path(__file__).with_name("taxonomy.yaml")
    raw = yaml.load(taxonomy_path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    if not isinstance(raw, dict):
        raise ValueError("taxonomy root must be a mapping")
    return Taxonomy.model_validate(raw)
