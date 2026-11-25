"""Preview or apply the community actor update to published Agroforestry data."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict

from sqlalchemy import func, select, text

from src.controlled_vocabulary import (
    COMMUNITY_ACTOR_RULE_ID,
    community_actor_name,
    join_community_actor_mentions,
)
from src.models.canonical_entities import CanonicalEntity
from src.models.canonical_entities_repo import CanonicalEntityRepo
from src.models.canonical_entity_aliases_repo import CanonicalEntityAliasRepo
from src.models.database import SessionLocal
from src.models.documents import Document
from src.models.entities import Entity
from src.services.fuzzy_matching import RESOLUTION_VERSION, normalizar_nombre


def evidence(row: Entity) -> dict:
    return {
        "id": str(row.id),
        "canonical_id": str(row.canonical_id),
        "text": row.text,
        "category": row.category,
        "sentence_id": row.sentence_id,
        "context": row.context,
        "ambiguity": row.ambiguity,
        "start": row.position_start,
        "end": row.position_end,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "resolution_method": row.resolution_method,
        "resolution_score": row.resolution_score,
        "resolution_version": row.resolution_version,
        "resolution_details": row.resolution_details,
    }


def update_published_actors(db, expected_digest: str | None) -> dict:
    if expected_digest:
        db.execute(text("SET LOCAL lock_timeout = '15s'"))
        db.execute(text(
            "LOCK TABLE documents, entities, canonical_entities, canonical_entity_aliases "
            "IN SHARE ROW EXCLUSIVE MODE"
        ))
    else:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))

    scope = select(Document.id).where(
        Document.status == "fuzzyMatching",
        Document.productive_sector == "Agroforestry",
    )
    document_ids = db.scalars(scope).all()
    rows = db.scalars(select(Entity).where(Entity.document_id.in_(scope)).order_by(Entity.id)).all()
    by_id = {str(row.id): row for row in rows}
    by_document = defaultdict(list)
    canonical_actors = db.scalars(select(CanonicalEntity).where(
        CanonicalEntity.category == "CHAR",
    ).order_by(CanonicalEntity.id))
    targets = {item.canonical_name: item for item in canonical_actors}

    for row in rows:
        by_document[row.document_id].append(evidence(row))

    plan = []
    variants = defaultdict(Counter)
    documents = defaultdict(set)
    for document_id, mentions in by_document.items():
        for mention in join_community_actor_mentions(mentions):
            name = community_actor_name(mention["text"], mention["category"], mention["context"])
            if name is None:
                continue
            variants[name][mention["text"]] += 1
            documents[name].add(document_id)
            row = by_id[mention["id"]]
            target = targets.get(name)
            sources = mention.get("_community_source_mentions")
            if sources or row.category != "CHAR" or target is None or row.canonical_id != target.id:
                plan.append((name, mention, sources or [mention], str(target.id) if target else None))

    digest = hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if expected_digest and expected_digest != digest:
        raise ValueError(f"El plan de AWS cambió. Esperado {expected_digest}, encontrado {digest}")

    if expected_digest:
        for name, mention, sources, _ in plan:
            target = targets.get(name)
            if target is None:
                target = CanonicalEntityRepo.crear(db, canonical_name=name, category="CHAR")
                targets[name] = target
            row = by_id[mention["id"]]
            row.canonical_id = target.id
            row.category = "CHAR"
            row.text = mention["text"]
            row.position_end = mention["end"]
            row.resolution_method = "controlled_alias"
            row.resolution_score = 100.0
            row.resolution_version = RESOLUTION_VERSION
            row.resolution_details = {
                "rule": COMMUNITY_ACTOR_RULE_ID,
                "preferred_name": name,
                "strategy": "community_actor",
                "source_mentions": sources,
            }
            for source in sources[1:]:
                db.delete(by_id[source["id"]])
            CanonicalEntityAliasRepo.registrar(
                db, canonical_id=target.id, alias_text=row.text,
                normalized_alias=normalizar_nombre(row.text), resolution_method="controlled_alias",
                source_document_id=row.document_id,
            )
        db.flush()
        expected_counts = {targets[name].id: sum(forms.values()) for name, forms in variants.items()}
        actual_counts = dict(db.execute(
            select(Entity.canonical_id, func.count())
            .where(Entity.document_id.in_(scope), Entity.canonical_id.in_(expected_counts))
            .group_by(Entity.canonical_id)
        ).all())
        if actual_counts != expected_counts:
            raise ValueError(f"Los recuentos posteriores difieren del plan: {actual_counts}")
        db.commit()

    return {
        "applied": bool(expected_digest),
        "digest": digest,
        "scope_documents": len(document_ids),
        "updated_rows": len(plan),
        "joint_repairs": sum(len(sources) > 1 for _, _, sources, _ in plan),
        "absorbed_rows": sum(len(sources) - 1 for _, _, sources, _ in plan),
        "groups": {
            name: {
                "id": str(targets[name].id) if name in targets else None,
                "mentions": sum(forms.values()),
                "documents": len(documents[name]),
                "forms": dict(forms.most_common()),
            }
            for name, forms in sorted(variants.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-digest", help="Digest from a preview against the same database")
    args = parser.parse_args()
    with SessionLocal() as db:
        result = update_published_actors(db, args.apply_digest)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
