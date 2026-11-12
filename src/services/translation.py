"""Auditable, segment-preserving translation of cleaned documents to English."""

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from src.config import settings
from src.services.llm_client import get_anthropic_client

logger = logging.getLogger(__name__)

TOOL_NAME = "submit_translation"
MAX_SEGMENTS_PER_REQUEST = 10
MAX_OUTPUT_TOKENS = 8192

TRANSLATION_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Report language verification and, for translation tasks, every English segment."
    ),
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "source_language_detected": {"type": "string"},
            "language_matches_metadata": {"type": "boolean"},
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "segment_id": {"type": "string"},
                        "text": {"type": "string"},
                    },
                    "required": ["segment_id", "text"],
                },
            },
        },
        "required": [
            "source_language_detected",
            "language_matches_metadata",
            "translations",
        ],
    },
}


class TranslationError(Exception):
    pass


class LanguageMismatchError(TranslationError):
    pass


@dataclass(frozen=True)
class Segment:
    segment_id: str
    text: str


def _split_long_paragraph(text: str, max_chars: int) -> list[str]:
    """Split oversized paragraphs at sentence or word boundaries."""
    pieces: list[str] = []
    remaining = text
    while len(remaining) > max_chars:
        prefix = remaining[: max_chars + 1]
        sentence_breaks = [
            match.end()
            for match in re.finditer(r"[.!?][ \t\n]+", prefix)
            if max_chars // 2 <= match.end() <= max_chars
        ]
        whitespace_breaks = [
            match.end()
            for match in re.finditer(r"[ \t\n]+", prefix)
            if max_chars // 2 <= match.end() <= max_chars
        ]
        cut = (sentence_breaks or whitespace_breaks or [None])[-1]
        if cut is None or cut > max_chars:
            raise TranslationError(
                "Un párrafo contiene una secuencia demasiado larga sin espacio para dividirla"
            )
        pieces.append(remaining[:cut])
        remaining = remaining[cut:]
    if remaining:
        pieces.append(remaining)
    return pieces


def _make_parts(text: str, max_chars: int) -> list[Segment | str]:
    parts: list[Segment | str] = []
    next_id = 1
    for paragraph in re.split(r"(\n[ \t]*\n+)", text):
        if not paragraph or not paragraph.strip():
            parts.append(paragraph)
            continue
        leading = paragraph[: len(paragraph) - len(paragraph.lstrip())]
        trailing = paragraph[len(paragraph.rstrip()) :]
        body = paragraph.strip()
        if leading:
            parts.append(leading)
        for piece in _split_long_paragraph(body, max_chars):
            content = piece.rstrip()
            if content:
                parts.append(Segment(f"s{next_id:05d}", content))
                next_id += 1
            suffix = piece[len(content) :]
            if suffix:
                parts.append(suffix)
        if trailing:
            parts.append(trailing)
    return parts


def _group_segments(parts: list[Segment | str], max_chars: int) -> list[list[Segment]]:
    groups: list[list[Segment]] = []
    current: list[Segment] = []
    current_chars = 0
    for part in parts:
        if not isinstance(part, Segment):
            continue
        if current and (
            current_chars + len(part.text) > max_chars
            or len(current) >= MAX_SEGMENTS_PER_REQUEST
        ):
            groups.append(current)
            current = []
            current_chars = 0
        current.append(part)
        current_chars += len(part.text)
    if current:
        groups.append(current)
    return groups


def _numbers(text: str) -> Counter[str]:
    return Counter(
        "".join(char for char in token if char.isdigit())
        for token in re.findall(r"\d+(?:[.,]\d+)*", text)
    )


def _validate_translation(payload: object, segments: list[Segment]) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise TranslationError("Respuesta de traducción sin estructura válida")
    detected = payload.get("source_language_detected")
    if not isinstance(detected, str) or not detected.strip():
        raise TranslationError("La respuesta no indicó el idioma detectado")
    matches = payload.get("language_matches_metadata")
    if matches is False:
        raise LanguageMismatchError(
            f"El idioma detectado ({detected}) no coincide con el registrado"
        )
    if matches is not True:
        raise TranslationError("La respuesta no verificó el idioma registrado")
    rows = payload.get("translations")
    if not isinstance(rows, list) or len(rows) != len(segments):
        raise TranslationError("Faltan segmentos en la respuesta de traducción")
    expected = {segment.segment_id: segment for segment in segments}
    translated: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise TranslationError("Segmento de traducción inválido")
        segment_id = row.get("segment_id")
        output = row.get("text")
        if segment_id not in expected or segment_id in translated:
            raise TranslationError("Identificador de segmento ausente o duplicado")
        if not isinstance(output, str) or not output.strip():
            raise TranslationError(f"Traducción vacía en {segment_id}")
        source = expected[segment_id].text
        if len(source) >= 80 and not 0.25 <= len(output) / len(source) <= 4:
            raise TranslationError(f"Longitud sospechosa en {segment_id}")
        if _numbers(source) != _numbers(output):
            raise TranslationError(f"Cifras alteradas u omitidas en {segment_id}")
        translated[segment_id] = output.strip()
    return translated


def verify_english_language(text: str) -> None:
    """Check a representative sample before copying an English file unchanged."""
    if not text.strip():
        raise TranslationError("El archivo limpio está vacío")
    if not settings.ANTHROPIC_API_KEY:
        raise TranslationError("ANTHROPIC_API_KEY no está configurada")
    prompt_path = Path(settings.TRANSLATION_PROMPT_PATH)
    if not prompt_path.is_file():
        raise TranslationError(f"Prompt de traducción no encontrado: {prompt_path}")
    if len(text) <= 6000:
        samples = [text]
    else:
        middle = len(text) // 2
        samples = [text[:2000], text[middle - 1000 : middle + 1000], text[-2000:]]
    target = {
        "task": "verify_language",
        "source_language": "en",
        "target_language": "en",
        "segments": [
            {"segment_id": f"sample_{index}", "text": sample}
            for index, sample in enumerate(samples, start=1)
        ],
    }
    system_prompt = prompt_path.read_text(encoding="utf-8")
    try:
        response = get_anthropic_client().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=256,
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(target, ensure_ascii=False)}],
            tools=[TRANSLATION_TOOL],
            tool_choice={"type": "tool", "name": TOOL_NAME},
        )
    except Exception as exc:
        logger.exception("Falló la verificación del idioma inglés")
        raise TranslationError(
            f"Error del proveedor al verificar idioma: {type(exc).__name__}"
        ) from exc
    if response.stop_reason == "max_tokens":
        raise TranslationError("Respuesta truncada al verificar idioma")
    payload = next(
        (
            block.input
            for block in response.content
            if getattr(block, "type", None) == "tool_use"
            and getattr(block, "name", None) == TOOL_NAME
        ),
        None,
    )
    if not isinstance(payload, dict):
        raise TranslationError("La verificación de idioma no usó la herramienta requerida")
    detected = payload.get("source_language_detected")
    if not isinstance(detected, str) or not detected.strip():
        raise TranslationError("La verificación no indicó el idioma detectado")
    if payload.get("language_matches_metadata") is False:
        raise LanguageMismatchError(
            f"El idioma detectado ({detected}) no coincide con el registrado (en)"
        )
    if payload.get("language_matches_metadata") is not True:
        raise TranslationError("La respuesta no verificó el idioma registrado")
    if payload.get("translations") != []:
        raise TranslationError("La verificación de idioma devolvió texto inesperado")


def translate_to_english(
    text: str, source_language: str, *, document_title: str = ""
) -> str:
    """Translate all segments or fail without returning a partial document."""
    if not text.strip():
        raise TranslationError("El archivo limpio está vacío")
    if not settings.ANTHROPIC_API_KEY:
        raise TranslationError("ANTHROPIC_API_KEY no está configurada")
    prompt_path = Path(settings.TRANSLATION_PROMPT_PATH)
    if not prompt_path.is_file():
        raise TranslationError(f"Prompt de traducción no encontrado: {prompt_path}")
    system_prompt = prompt_path.read_text(encoding="utf-8")
    max_chars = settings.TRANSLATION_MAX_CHUNK_CHARS
    if max_chars < 1000:
        raise TranslationError("TRANSLATION_MAX_CHUNK_CHARS debe ser al menos 1000")
    parts = _make_parts(text, max_chars)
    groups = _group_segments(parts, max_chars)
    translations: dict[str, str] = {}
    client = get_anthropic_client()
    logger.info("Traduciendo %d segmentos en %d solicitudes", sum(map(len, groups)), len(groups))

    for index, segments in enumerate(groups, start=1):
        target = {
            "task": "translate",
            "source_language": source_language,
            "target_language": "en",
            "document_title": document_title,
            "document_context_excerpt": text[:1200],
            "segments": [
                {"segment_id": segment.segment_id, "text": segment.text}
                for segment in segments
            ],
        }
        try:
            response = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": json.dumps(target, ensure_ascii=False)}],
                tools=[TRANSLATION_TOOL],
                tool_choice={"type": "tool", "name": TOOL_NAME},
            )
        except Exception as exc:
            logger.exception("Falló la llamada de traducción en bloque %d", index)
            raise TranslationError(
                f"Error del proveedor en bloque {index}: {type(exc).__name__}"
            ) from exc
        if response.stop_reason == "max_tokens":
            raise TranslationError(f"Respuesta truncada en bloque {index}")
        payload = next(
            (
                block.input
                for block in response.content
                if getattr(block, "type", None) == "tool_use"
                and getattr(block, "name", None) == TOOL_NAME
            ),
            None,
        )
        translations.update(_validate_translation(payload, segments))

    return "".join(
        translations[part.segment_id] if isinstance(part, Segment) else part
        for part in parts
    )
