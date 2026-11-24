"""Editorial vocabulary decisions; literal evidence remains unchanged."""
import re
import unicodedata

# All SAF/SAFs variants and compounds were explicitly excluded on Nov 24.
# Keep the observed labels reviewable and recognize the acronym as a whole
# token so future suffixes are covered without matching safe/safety/SAFTA.
SAF_EXCLUDED_ENTITY_NAMES = (
    "SAF", "SAFs", "SAFs-A", "SAFs-F",
    "SAF-dendê", "SAFs-A variant",
    *(f"SAF {number}" for number in range(1, 15)),
    *(f"SAF type {number}" for number in ("I", "II", "III", "IV")),
    "SAF implementation", "SAF establishment", "SAF Incubator", "SAF arrangements",
    "SAF design", "Designs of the two SAFs", "SAF adoption", "SAF management",
    "Agroforestry Systems (SAF)", "SAF economy", "SAF living laboratory",
    "Establishing these plots under the SAF approach",
    "intercropping cacao or coffee with other perennial plants in diversified SAFs",
    "unique SAF-related characteristics",
)


def is_saf_entity_name(value: str) -> bool:
    """Recognize the SAF acronym anywhere in an entity label, not substrings."""
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(c for c in value if not unicodedata.combining(c))
    return bool(
        re.search(r"(?<![a-z0-9])s[.\s]*a[.\s]*f\.?s?(?![a-z0-9])", value)
        or re.fullmatch(r"safs[af]", value.strip())
    )


ROAD_CANONICAL_NAME = "road pavement"
ROAD_CANONICAL_CATEGORY = "physical_INFRA"
ROAD_RULE_ID = "road-pavement-2026-11-24"

# Exclusions take precedence over canonicalization: these names stay outside
# the explorer and must not reappear under the new preferred name.
ROAD_EXCLUDED_ENTITY_NAMES = (
    "roads", "road construction", "Leticia-Tarapaca road", "new road",
    "new roads", "Transamazonica Road Region",
)


def _name_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return "".join(char for char in value if char.isalnum())


_ROAD_EXCLUSION_KEYS = frozenset(map(_name_key, ROAD_EXCLUDED_ENTITY_NAMES))


def is_road_pavement_alias(value: str) -> bool:
    """Match the words road/roads, respecting prior whole-name exclusions.

    This is an explicit editorial grouping, not a claim of lexical synonymy.
    Roadmap, railroads, broad and broadcast are separate words.
    """
    if _name_key(value) in _ROAD_EXCLUSION_KEYS:
        return False
    return bool(re.search(r"\broads?\b", value.casefold().replace("_", " ")))
