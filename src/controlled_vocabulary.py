"""Editorial vocabulary decisions; literal evidence remains unchanged."""
import re
import unicodedata
from collections import defaultdict
from typing import Any

INDIGENOUS_PEOPLES = "Indigenous Peoples"
LOCAL_COMMUNITIES = "local communities"
JOINT_COMMUNITIES = "IPLCs"
COMMUNITY_ACTOR_NAMES = (INDIGENOUS_PEOPLES, LOCAL_COMMUNITIES, JOINT_COMMUNITIES)
COMMUNITY_ACTOR_RULE_ID = "indigenous-peoples-local-communities"

_IP = r"ips?"
_LC = r"lcs?"
_IP_NAME = (r"indigenou(?:s)?(?:\s+(?:peoples?(?:\s+groups?)?|communit(?:y|ies)|"
            r"populations?|groups?|nations?))?|(?:pueblos?|povos?)\s+indigenas?|indigenas?")
_LC_NAME = r"local\s+communit(?:y|ies|ie)|comunidades?\s+loca(?:l|les|is)"
_IP_TERM = rf"(?:(?:{_IP_NAME})(?:\s*\({_IP}\))?|{_IP})"
_LC_TERM = rf"(?:(?:{_LC_NAME})(?:\s*\({_LC}\))?|{_LC})"
_JOIN = r"['’]?\s*(?:\band\b|\by\b|\be\b|&|/|\+)\s*(?:(?:the|las|los|as|os)\s+)?"
_JOINT_COMMUNITIES = re.compile(
    rf"(?:iplcs?|(?:{_IP_TERM}{_JOIN}{_LC_TERM}|{_LC_TERM}{_JOIN}{_IP_TERM}|"
    rf"indigenous{_JOIN}local\s+peoples?|local{_JOIN}(?:native|indigenous)\s+communities)"
    rf"['’]?(?:\s*\(iplcs?\))?)"
)
_INDIGENOUS_PEOPLES = re.compile(
    rf"(?:{_IP_TERM}|(?:local|enslaved)\s+indigenous\s+(?:peoples?|communities)|"
    r"indigenous\s+(?:ethnic groups?|communit(?:y|ies) members?|women(?: and youth)?|"
    r"leaders?(?: \(men and women\))?|youth|families|farmers|farming families|"
    r"scientists|specialists|members|authorities|participants?))"
)
_LOCAL_COMMUNITIES = re.compile(_LC_TERM)
_OTHER_IP_EXPANSIONS = (
    ("social progress index", "Social Progress Index"),
    ("intellectual property", "Intellectual Property"),
    ("internet protocol", "Internet Protocol"),
)


def _community_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    normalized = re.sub(r"(?<!\w)(?:i\.p\.?l\.c\.?|i\.p\.?|l\.c\.?)(?:s\b)?(?!\w)",
                        lambda match: match[0].replace(".", ""), normalized)
    return re.sub(r"^(?:(?:the|las|los|as|os|ten|seven|\d+)\s+)+", "", normalized)


def community_actor_name(text: str, category: str, context: str | None = None) -> str | None:
    """Map an actor mention by its own text, retaining evidence of other IP expansions."""
    key = _community_key(text).rstrip("'’")
    if category != "CHAR":
        # The complete actor phrases remain unambiguous when NER mistags them.
        if not re.fullmatch(rf"(?:{_IP_NAME}|{_LC_NAME})", key) or " " not in key:
            return None
    if re.fullmatch(_IP, key) and context:
        sentence = _community_key(context)
        for expansion, name in _OTHER_IP_EXPANSIONS:
            if re.search(rf"\b{expansion}\s*\({key}\b", sentence):
                return name
    if _JOINT_COMMUNITIES.fullmatch(key):
        return JOINT_COMMUNITIES
    if _LOCAL_COMMUNITIES.fullmatch(key):
        return LOCAL_COMMUNITIES
    if _INDIGENOUS_PEOPLES.fullmatch(key):
        return INDIGENOUS_PEOPLES
    return None


def join_community_actor_mentions(mentions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Repair split annotations only when an exact source span names both actors."""
    by_sentence: dict[str, list[int]] = defaultdict(list)
    for index, mention in enumerate(mentions):
        if isinstance(mention.get("sentence_id"), str):
            by_sentence[mention["sentence_id"]].append(index)

    replacements: dict[int, dict[str, Any]] = {}
    absorbed: set[int] = set()
    for sentence_id, indices in by_sentence.items():
        sentence = re.fullmatch(r"s-(\d+)", sentence_id)
        if sentence is None:
            continue
        offset = int(sentence[1])
        indices.sort(key=lambda index: mentions[index]["start"] if mentions[index]["start"] is not None else -1)
        for position, index in enumerate(indices):
            first = mentions[index]
            context, start = first.get("context"), first["start"]
            if (index in absorbed or not isinstance(context, str) or start is None
                    or community_actor_name(first["text"], first["category"], context)
                    not in {INDIGENOUS_PEOPLES, LOCAL_COMMUNITIES}):
                continue
            parts: list[int] = []
            best: tuple[list[int], int] | None = None
            previous_end = start
            for part_index in indices[position:position + 5]:
                part = mentions[part_index]
                part_start, end = part["start"], part["end"]
                if (part.get("context") != context or part_start is None or end is None
                        or not offset <= previous_end <= part_start < end <= offset + len(context)
                        or context[part_start-offset:end-offset] != part["text"]
                        or community_actor_name(part["text"], part["category"], context)
                        not in COMMUNITY_ACTOR_NAMES
                        or end - start > 150):
                    break
                parts.append(part_index)
                previous_end = end
                if len(parts) < 2:
                    continue
                # An acronym annotation can end inside its parentheses.
                candidate_end = end + (context[end-offset:end-offset+1] == ")")
                for span_end in range(candidate_end, end - 1, -1):
                    if community_actor_name(context[start-offset:span_end-offset], "CHAR", context) == JOINT_COMMUNITIES:
                        best = (parts.copy(), span_end)
                        break
            if best is None:
                continue
            parts, end = best
            # A historic overlapping annotation may extend past the span.
            if any(mentions[other]["start"] is not None and mentions[other]["end"] is not None
                   and mentions[other]["start"] < end and mentions[other]["end"] > start
                   for other in indices if other not in parts):
                continue
            replacements[index] = {
                **first, "text": context[start-offset:end-offset], "end": end,
                "_community_source_mentions": [mentions[part] for part in parts],
            }
            absorbed.update(parts[1:])
    return [replacements.get(index, mention) for index, mention in enumerate(mentions)
            if index not in absorbed]

BRAZIL_NUT_CANONICAL_NAME = "Brazil nut"
BRAZIL_NUT_CANONICAL_CATEGORY = "eco_INFRA"
BRAZIL_NUT_RULE_ID = "brazil-nut-contextual-span-2026-11-24"
_BRAZIL_NUT = re.compile(r"(?<!\w)brazi(?:l)?(?:\s+|[‐‑‒–—-]\s*)nuts?(?!\w)", re.IGNORECASE)


def is_brazil_nut_name(value: str) -> bool:
    """Only the complete resource name, never Brazil or harvesting compounds."""
    return _BRAZIL_NUT.fullmatch(value.strip()) is not None


def brazil_nut_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Complete an anchored Brazi/Brazil span only when the source says nut(s).

    The exact occurrence matters: the same sentence can mention the country
    and its nut. Never infer the resource merely from nearby words.
    """
    if not 0 <= start < end <= len(text):
        return None
    match = _BRAZIL_NUT.match(text, start)
    if match is None:
        return None
    if (start, end) == match.span() or text[start:end].casefold() in {"brazi", "brazil"}:
        return match.span()
    return None

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
