-- Additive batch schema; installed transactionally by process_metanetworks.py.
-- Version: agroforestry-metanetworks-v1. No changes to corpus or legacy tables.
CREATE TABLE IF NOT EXISTS metanetwork_runs (
    id uuid PRIMARY KEY,
    schema_version text NOT NULL CHECK (schema_version = 'agroforestry-metanetworks-v1'),
    productive_sector text NOT NULL CHECK (productive_sector = 'Agroforestry'),
    source_sha256 text NOT NULL,
    document_ids jsonb NOT NULL,
    configuration jsonb NOT NULL,
    artifact_path text NOT NULL UNIQUE,
    artifact_hashes jsonb NOT NULL,
    summary jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metanetwork_nodes (
    id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES metanetwork_runs(id) ON DELETE RESTRICT,
    network_id text NOT NULL CHECK (network_id IN ('network1','network2','network3')),
    community_id text NOT NULL,
    canonical_name text NULL,
    description text NULL,
    vector vector NULL,
    vector_method_version text NULL,
    provenance jsonb NOT NULL,
    document_count integer NOT NULL CHECK (document_count >= 0),
    member_count integer NOT NULL CHECK (member_count > 0),
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, network_id, community_id),
    UNIQUE (id, run_id, network_id)
);

CREATE TABLE IF NOT EXISTS metanetwork_node_members (
    node_id uuid NOT NULL,
    run_id uuid NOT NULL,
    network_id text NOT NULL,
    canonical_id uuid NOT NULL REFERENCES canonical_entities(id) ON DELETE RESTRICT,
    canonical_name text NOT NULL,
    category text NOT NULL,
    evidence jsonb NOT NULL,
    PRIMARY KEY (node_id, canonical_id),
    UNIQUE (run_id, network_id, canonical_id),
    FOREIGN KEY (node_id, run_id, network_id)
      REFERENCES metanetwork_nodes(id, run_id, network_id) ON DELETE RESTRICT,
    CHECK (
      (network_id = 'network1' AND category IN ('CHAR','KNOW','ATT','SKILL')) OR
      (network_id = 'network2' AND category IN ('CHAR','PRAC','KNOW','RUL')) OR
      (network_id = 'network3' AND category IN ('CHAR','PRAC','physical_INFRA','soft_INFRA','eco_INFRA'))
    )
);
CREATE INDEX IF NOT EXISTS ix_metanetwork_nodes_run_network
  ON metanetwork_nodes(run_id, network_id);
CREATE INDEX IF NOT EXISTS ix_metanetwork_members_canonical
  ON metanetwork_node_members(canonical_id);
