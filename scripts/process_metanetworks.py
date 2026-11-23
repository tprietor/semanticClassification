"""Versioned Agroforestry backbone/Leiden batches; additive PostgreSQL storage.

Run from the project root with PYTHONPATH=.: prepare, then publish, then verify.
prepare writes only a new artifact directory. publish checks the live source
against the captured snapshot and installs/inserts new tables in one transaction.
No document, mention, canonical, legacy graph, or NER file is updated.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4, uuid5

import networkx as nx
import psycopg2
from psycopg2.extras import Json, RealDictCursor, execute_values

from src.analysis.backbone import (
    DocumentRecurrentCoreConfig, build_document_recurrent_core,
    export_backbone_to_files,
)
from src.analysis.cooccurrence import MentionRecord, build_sentence_cooccurrence
from src.analysis.leiden import LeidenConfig, export_leiden_clustering

VERSION = "agroforestry-metanetworks-v1"
NETWORKS = {
    "network1": ("CHAR", "KNOW", "ATT", "SKILL"),
    "network2": ("CHAR", "PRAC", "KNOW", "RUL"),
    "network3": ("CHAR", "PRAC", "physical_INFRA", "soft_INFRA", "eco_INFRA"),
}
CONFIG = {
    "backbone": asdict(DocumentRecurrentCoreConfig(minimum_node_document_count=1)),
    "leiden": asdict(LeidenConfig()),
    "component_scope": "all-components",
    "initial_edge_definition": "same_document_same_sentence_cooccurrence",
    "allowed_category_pairs": "all unordered pairs, including same category",
    "excluded_canonical_names": ["agroforestry", "madre de dios"],
    "metanetwork_edges": "deferred_until_vector_method_is_defined",
}


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def connect():
    return psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=15)


def capture(conn, expected_documents=48):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""SELECT id::text,original_filename,status,productive_sector,
            language,year,incubator_number,document_type FROM documents
            WHERE productive_sector='Agroforestry' AND status='fuzzyMatching'
            ORDER BY id""")
        documents = [dict(row) for row in cur.fetchall()]
        if len(documents) != expected_documents:
            raise ValueError(f"Expected {expected_documents} source documents, got {len(documents)}")
        cur.execute("""SELECT e.id::text AS mention_id,e.document_id::text,
            e.canonical_id::text,c.canonical_name,c.category AS canonical_category,
            e.category,e.text,e.position_start AS start,e.position_end AS end,
            e.sentence_id,e.context,e.ambiguity,s.text AS sentence_text
            FROM entities e JOIN documents d ON d.id=e.document_id
            JOIN canonical_entities c ON c.id=e.canonical_id
            LEFT JOIN sentences s ON s.document_id=e.document_id AND s.sentence_id=e.sentence_id
            WHERE d.productive_sector='Agroforestry' AND d.status='fuzzyMatching'
            ORDER BY e.id""")
        mentions = [dict(row) for row in cur.fetchall()]
    if not mentions:
        raise ValueError("No canonicalized mentions")
    if {m["document_id"] for m in mentions} != {d["id"] for d in documents}:
        raise ValueError("Some selected documents lack canonicalized mentions")
    for row in mentions:
        if row["category"] != row["canonical_category"] or not row["sentence_text"]:
            raise ValueError(f"Missing sentence evidence or category mismatch: {row['mention_id']}")
    return {"documents": documents, "mentions": mentions}


def records(snapshot):
    excluded = set(CONFIG["excluded_canonical_names"])
    return [MentionRecord(**{k: m[k] for k in (
        "document_id", "sentence_id", "canonical_id", "canonical_name", "category",
        "text", "start", "end", "context", "ambiguity", "mention_id")})
        for m in snapshot["mentions"]
        if " ".join(m["canonical_name"].casefold().split()) not in excluded]


def build_network(snapshot, network_id, output, run_id):
    output.mkdir(parents=True, exist_ok=False)
    source = build_sentence_cooccurrence(records(snapshot), node_categories=NETWORKS[network_id])
    write_json(output / "initial_network.json", {
        "nodes": [asdict(n) for n in source.nodes],
        "links": [{"source": source.nodes[a].canonical_id,
                   "target": source.nodes[b].canonical_id,
                   "sentence_count": count,
                   "document_count": len(source.edge_documents[(a, b)])}
                  for (a, b), count in sorted(source.edge_weights.items())],
        "edge_definition": CONFIG["initial_edge_definition"],
    })
    backbone = build_document_recurrent_core(source, DocumentRecurrentCoreConfig(**CONFIG["backbone"]))
    # All connected components are retained; the existing backbone excludes isolates.
    export_backbone_to_files(backbone, graphml_path=output / "backbone.graphml",
        nodes_csv_path=output / "entities.csv", edges_csv_path=output / "cooccurrences.csv",
        json_path=output / "backbone.json", metadata={"configuration": CONFIG["backbone"]})
    excluded = {"nodes": list(backbone.excluded_nodes), "edges": list(backbone.excluded_edges)}
    write_json(output / "excluded.json", excluded)
    partition = export_leiden_clustering(output / "backbone.graphml", output,
        config=LeidenConfig(), base_name="leiden")
    graph = nx.read_graphml(output / "leiden.graphml")
    groups = defaultdict(list)
    evidence_by_canonical = defaultdict(list)
    for mention in snapshot["mentions"]:
        evidence_by_canonical[mention["canonical_id"]].append(mention)
    for canonical_id, attributes in graph.nodes(data=True):
        groups[attributes["community_id"]].append(canonical_id)
    nodes = []
    source_hash = digest(snapshot)
    for community_id, ids in sorted(groups.items()):
        members = []
        docs = set()
        for canonical_id in sorted(ids):
            attributes = graph.nodes[canonical_id]
            evidence = evidence_by_canonical[canonical_id]
            docs.update(m["document_id"] for m in evidence)
            members.append({"canonical_id": canonical_id,
                "canonical_name": attributes["canonical_name"],
                "category": attributes["category"], "evidence": evidence})
        nodes.append({"id": str(uuid5(UUID(run_id), network_id + ":" + community_id)),
            "network_id": network_id, "community_id": community_id,
            "canonical_name": None, "description": None, "vector": None,
            "vector_method_version": None, "document_count": len(docs),
            "member_count": len(members), "members": members,
            "provenance": {"source_sha256": source_hash,
                "backbone_sha256": hashlib.sha256((output / "backbone.graphml").read_bytes()).hexdigest(),
                "partition_sha256": hashlib.sha256((output / "leiden.graphml").read_bytes()).hexdigest(),
                "configuration": CONFIG, "categories": NETWORKS[network_id],
                "document_ids": sorted(docs), "community_id": community_id}})
    write_json(output / "clusters.json", {"nodes": nodes, "links": [],
        "edge_method": "vector_similarity_pending"})
    summary = {"categories": NETWORKS[network_id], "initial_entities": len(source.nodes),
        "backbone_entities": graph.number_of_nodes(), "backbone_edges": graph.number_of_edges(),
        "components": nx.number_connected_components(graph), "clusters": len(nodes),
        "cluster_sizes": sorted([n["member_count"] for n in nodes], reverse=True),
        "excluded_entities": len(backbone.excluded_nodes),
        "category_counts": dict(Counter(a["category"] for _, a in graph.nodes(data=True))),
        "modularity": partition["modularity"], "metanetwork_edges": 0}
    return summary


def artifact_hashes(output):
    return {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()
            and p.name not in {"manifest.json", "publication.json", "verification.json"}}


def validate_configuration(configuration):
    # Permit verification of the immutable first run, which used threshold 2.
    # New runs always use CONFIG (threshold 1, no cross-document recurrence filter).
    expected = {**CONFIG, "backbone": dict(CONFIG["backbone"])}
    threshold = configuration.get("backbone", {}).get("minimum_node_document_count")
    if threshold not in (1, 2):
        raise ValueError("Unsupported document threshold")
    expected["backbone"]["minimum_node_document_count"] = threshold
    if configuration != expected:
        raise ValueError("Unsupported or changed configuration")


def validate_bundle(output):
    manifest = json.loads((output / "manifest.json").read_text())
    if manifest["schema_version"] != VERSION:
        raise ValueError("Unsupported schema version")
    validate_configuration(manifest["configuration"])
    if manifest["artifact_hashes"] != artifact_hashes(output):
        raise ValueError("Artifact hash mismatch")
    with gzip.open(output / "source.json.gz", "rt", encoding="utf-8") as file:
        source = json.load(file)
    if manifest["source_sha256"] != digest(source):
        raise ValueError("Source fingerprint mismatch")
    all_nodes = []
    for network_id, categories in NETWORKS.items():
        payload = json.loads((output / network_id / "clusters.json").read_text())
        if payload["links"]:
            raise ValueError("Vector connections must remain empty")
        seen = set()
        graph = nx.read_graphml(output / network_id / "leiden.graphml")
        for node in payload["nodes"]:
            if node["network_id"] != network_id or any(node[k] is not None for k in
                    ("canonical_name", "description", "vector", "vector_method_version")):
                raise ValueError("Invalid network or non-null deferred metadata")
            if node["member_count"] != len(node["members"]) or not node["members"]:
                raise ValueError("Invalid member count")
            if node["provenance"]["configuration"] != manifest["configuration"]:
                raise ValueError("Cluster/manifest configuration mismatch")
            expected_id = str(uuid5(UUID(manifest["run_id"]), network_id + ":" + node["community_id"]))
            if node["id"] != expected_id:
                raise ValueError("Invalid global UUID")
            for member in node["members"]:
                cid = member["canonical_id"]
                if cid in seen or member["category"] not in categories:
                    raise ValueError("Duplicate membership or wrong category")
                seen.add(cid)
                if graph.nodes[cid]["community_id"] != node["community_id"]:
                    raise ValueError("Partition/member mismatch")
                if not member["evidence"]:
                    raise ValueError("Missing evidence")
            all_nodes.append(node)
        if seen != set(graph.nodes):
            raise ValueError("Partition coverage mismatch")
    return manifest, source, all_nodes


def prepare(output, run_id, expected_documents):
    output.mkdir(parents=True, exist_ok=False)
    with connect() as conn:
        conn.set_session(readonly=True, isolation_level="REPEATABLE READ")
        snapshot = capture(conn, expected_documents)
    with gzip.open(output / "source.json.gz", "wt", encoding="utf-8") as file:
        json.dump(snapshot, file, ensure_ascii=False)
    (output / "processor.py").write_bytes(Path(__file__).read_bytes())
    schema = Path(__file__).parent / "sql/metanetworks_v1.sql"
    (output / "schema.sql").write_bytes(schema.read_bytes())
    summary = {}
    for network_id in NETWORKS:
        summary[network_id] = build_network(snapshot, network_id, output / network_id, run_id)
        print(json.dumps({"network": network_id, **summary[network_id]}), flush=True)
    manifest = {"run_id": run_id, "schema_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "productive_sector": "Agroforestry", "source_sha256": digest(snapshot),
        "document_ids": [d["id"] for d in snapshot["documents"]],
        "source_mentions": len(snapshot["mentions"]), "configuration": CONFIG,
        "implementation": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path("src/analysis/cooccurrence.py"), Path("src/analysis/backbone.py"),
             Path("src/analysis/leiden.py"), Path("src/categories.py")]},
        "artifact_path": str(output), "summary": summary,
        "artifact_hashes": artifact_hashes(output)}
    write_json(output / "manifest.json", manifest)
    validate_bundle(output)
    return manifest


def publish(output, schema_path):
    manifest, source, nodes = validate_bundle(output)
    with connect() as conn:
        conn.set_session(isolation_level="REPEATABLE READ")
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout='10s'")
            cur.execute("SET LOCAL statement_timeout='120s'")
            # Prevent concurrent mutation of the source while checking and publishing.
            cur.execute("LOCK TABLE documents,entities,canonical_entities,sentences IN SHARE MODE")
            cur.execute("SELECT pg_advisory_xact_lock(68723011202026)")
            if digest(capture(conn, len(source["documents"]))) != manifest["source_sha256"]:
                raise ValueError("AWS source changed since prepare; create a new run")
            cur.execute(schema_path.read_text())
            cur.execute("SELECT source_sha256,artifact_hashes FROM metanetwork_runs WHERE id=%s",
                        (manifest["run_id"],))
            previous = cur.fetchone()
            if previous:
                if previous != (manifest["source_sha256"], manifest["artifact_hashes"]):
                    raise ValueError("Run UUID already exists with different content")
            else:
                cur.execute("""INSERT INTO metanetwork_runs
                    (id,schema_version,productive_sector,source_sha256,document_ids,
                     configuration,artifact_path,artifact_hashes,summary)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (manifest["run_id"], VERSION, "Agroforestry", manifest["source_sha256"],
                     Json(manifest["document_ids"]), Json(manifest["configuration"]), str(output),
                     Json(manifest["artifact_hashes"]), Json(manifest["summary"])))
                execute_values(cur, """INSERT INTO metanetwork_nodes
                    (id,run_id,network_id,community_id,canonical_name,description,vector,
                     vector_method_version,provenance,document_count,member_count) VALUES %s""",
                    [(n["id"],manifest["run_id"],n["network_id"],n["community_id"],
                      None,None,None,None,Json(n["provenance"]),n["document_count"],n["member_count"])
                     for n in nodes])
                execute_values(cur, """INSERT INTO metanetwork_node_members
                    (node_id,run_id,network_id,canonical_id,canonical_name,category,evidence) VALUES %s""",
                    [(n["id"],manifest["run_id"],n["network_id"],m["canonical_id"],
                      m["canonical_name"],m["category"],Json(m["evidence"]))
                     for n in nodes for m in n["members"]], page_size=100)
            verify_rows(cur, manifest, nodes)
            if digest(capture(conn, len(source["documents"]))) != digest(source):
                raise ValueError("Source preservation check failed")
    receipt = {"run_id": manifest["run_id"], "committed_at": datetime.now(timezone.utc).isoformat(),
        "nodes": len(nodes), "members": sum(n["member_count"] for n in nodes),
        "source_unchanged": True, "deferred_metadata_is_null": True}
    write_json(output / "publication.json", receipt)
    return receipt


def verify_rows(cur, manifest, nodes):
    cur.execute("""SELECT id::text,network_id,community_id,member_count,document_count,
        canonical_name,description,vector,vector_method_version FROM metanetwork_nodes
        WHERE run_id=%s ORDER BY id""", (manifest["run_id"],))
    actual = cur.fetchall()
    expected = sorted([(n["id"],n["network_id"],n["community_id"],n["member_count"],
        n["document_count"],None,None,None,None) for n in nodes])
    if actual != expected:
        raise ValueError("PostgreSQL cluster metadata mismatch")
    cur.execute("""SELECT node_id::text,network_id,canonical_id::text,canonical_name,
        category,evidence FROM metanetwork_node_members WHERE run_id=%s
        ORDER BY node_id,canonical_id""", (manifest["run_id"],))
    expected_members = sorted([(n["id"],n["network_id"],m["canonical_id"],m["canonical_name"],
        m["category"],m["evidence"]) for n in nodes for m in n["members"]], key=lambda r:r[:3])
    if cur.fetchall() != expected_members:
        raise ValueError("PostgreSQL member/evidence mismatch")


def verify(output):
    manifest, source, nodes = validate_bundle(output)
    with connect() as conn:
        conn.set_session(readonly=True, isolation_level="REPEATABLE READ")
        with conn.cursor() as cur:
            verify_rows(cur, manifest, nodes)
        if digest(capture(conn, len(source["documents"]))) != manifest["source_sha256"]:
            raise ValueError("Live corpus differs from the recorded source")
    return {"run_id": manifest["run_id"], "verified": True, "summary": manifest["summary"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "publish", "verify"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--expected-documents", type=int, default=48)
    parser.add_argument("--schema", type=Path,
        default=Path(__file__).parent / "sql/metanetworks_v1.sql")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.output, str(UUID(args.run_id)) if args.run_id else str(uuid4()),
                         args.expected_documents)
    elif args.command == "publish":
        result = publish(args.output, args.schema)
    else:
        result = verify(args.output)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
