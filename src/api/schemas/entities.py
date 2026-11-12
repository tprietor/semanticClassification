from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EntityOut(BaseModel):
    text: str
    category: str
    start: int
    end: int
    sentence_id: str
    context: str | None = None
    ambiguity: str | None = None


class ExtractEntitiesResponse(BaseModel):
    document_id: str
    entities: list[EntityOut]


class MatchedEntityOut(EntityOut):
    canonical_id: UUID
    canonical_name: str
    match_type: str
    match_score: float
    second_match_score: float | None = None
    resolution_version: str
    resolution_details: dict[str, Any]


class FuzzyMatchingResponse(BaseModel):
    document_id: str
    entities: list[MatchedEntityOut]


class ResolvedEntityRead(BaseModel):
    id: UUID
    text: str
    category: str
    start: int | None
    end: int | None
    sentence_id: str | None
    context: str | None
    ambiguity: str | None
    canonical_id: UUID
    canonical_name: str
    canonical_category: str
    match_type: str | None
    match_score: float | None
    resolution_version: str | None
    resolution_details: dict[str, Any] | None


class ResolvedEntitiesResponse(BaseModel):
    document_id: UUID
    original_filename: str
    status: str
    language: str | None
    productive_sector: str | None
    document_total: int
    category_counts: dict[str, int]
    match_type_counts: dict[str, int]
    applied_filters: dict[str, str | None]
    total: int
    skip: int
    limit: int
    entities: list[ResolvedEntityRead]
