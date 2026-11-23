import copy
import json
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

import networkx as nx

from scripts.process_metanetworks import CONFIG, NETWORKS, build_network, records, validate_configuration


def fixture():
    """Two documents with category-spanning, disconnected evidence groups."""
    canonical_ids = {category: str(uuid4()) for category in
                     set(c for categories in NETWORKS.values() for c in categories)}
    mentions = []
    documents = [{"id": str(uuid4())} for _ in range(2)]
    for doc in documents:
        for group, categories in enumerate((
                ("CHAR", "KNOW", "ATT", "SKILL"),
                ("PRAC", "RUL", "physical_INFRA", "soft_INFRA", "eco_INFRA"))):
            for offset, category in enumerate(categories):
                mentions.append(dict(mention_id=str(uuid4()), document_id=doc["id"],
                    canonical_id=canonical_ids[category], canonical_name=category,
                    canonical_category=category, category=category, text=category,
                    start=offset * 20, end=offset * 20 + len(category),
                    sentence_id=f"s-{group}", context=f"evidence {group}",
                    sentence_text=f"evidence {group}", ambiguity="low"))
    return dict(documents=documents, mentions=mentions)


class MetanetworkBatchTests(unittest.TestCase):
    def test_single_document_entities_are_retained(self):
        source = fixture()
        source["documents"] = source["documents"][:1]
        source["mentions"] = [m for m in source["mentions"]
                              if m["document_id"] == source["documents"][0]["id"]]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "network1"
            summary = build_network(source, "network1", directory, str(uuid4()))
            self.assertEqual(set(summary["category_counts"]), set(NETWORKS["network1"]))
            self.assertEqual(summary["backbone_entities"], 4)
            exclusions = json.loads((directory / "excluded.json").read_text())
            self.assertEqual(exclusions["nodes"], [])
            nodes = json.loads((directory / "clusters.json").read_text())["nodes"]
            self.assertTrue(all(n["document_count"] == 1 for n in nodes))

    def test_archived_threshold_can_be_verified_without_changing_new_default(self):
        archived = copy.deepcopy(CONFIG)
        archived["backbone"]["minimum_node_document_count"] = 2
        validate_configuration(archived)
        self.assertEqual(CONFIG["backbone"]["minimum_node_document_count"], 1)
        changed = copy.deepcopy(CONFIG)
        changed["leiden"]["resolution"] = 2
        with self.assertRaises(ValueError):
            validate_configuration(changed)

    def test_three_category_projections_and_complete_cluster_membership(self):
        source = fixture()
        run_id = str(uuid4())
        with tempfile.TemporaryDirectory() as tmp:
            for network_id, categories in NETWORKS.items():
                with self.subTest(network=network_id):
                    directory = Path(tmp) / network_id
                    summary = build_network(source, network_id, directory, run_id)
                    payload = json.loads((directory / "clusters.json").read_text())
                    members = [m for n in payload["nodes"] for m in n["members"]]
                    expected_categories = set(categories)
                    if network_id == "network3":
                        # CHAR has no cooccurring partner in this projection.
                        expected_categories.remove("CHAR")
                    self.assertEqual({m["category"] for m in members}, expected_categories)
                    graph = nx.read_graphml(directory / "leiden.graphml")
                    self.assertEqual(len(members), len(graph))
                    self.assertEqual(len({m["canonical_id"] for m in members}), len(members))
                    self.assertEqual(payload["links"], [])
                    self.assertEqual(summary["metanetwork_edges"], 0)
                    if network_id == "network2":
                        self.assertEqual(summary["components"], 2)
                    if network_id == "network3":
                        exclusions = json.loads((directory / "excluded.json").read_text())
                        actor = next(n for n in exclusions["nodes"] if n["category"] == "CHAR")
                        self.assertEqual(actor["exclusion_reason"], "no_edge_to_another_eligible_node")
                    for node in payload["nodes"]:
                        for key in ("canonical_name", "description", "vector", "vector_method_version"):
                            self.assertIsNone(node[key])
                        self.assertEqual(node["document_count"], 2)
                        self.assertTrue(all(len(m["evidence"]) == 2 for m in node["members"]))

    def test_memberships_and_global_ids_survive_reordering(self):
        source = fixture()
        reordered = copy.deepcopy(source)
        reordered["mentions"].reverse()
        run_id = str(uuid4())
        with tempfile.TemporaryDirectory() as tmp:
            for label, snapshot in (("a", source), ("b", reordered)):
                build_network(snapshot, "network2", Path(tmp) / label, run_id)
            def partition(label):
                payload = json.loads((Path(tmp) / label / "clusters.json").read_text())
                return {n["id"]: sorted(m["canonical_id"] for m in n["members"])
                        for n in payload["nodes"]}
            self.assertEqual(partition("a"), partition("b"))

    def test_name_exclusions_do_not_mutate_source(self):
        source = fixture()
        source["mentions"][0]["canonical_name"] = "  AGROFORESTRY  "
        source["mentions"][1]["canonical_name"] = "Agroforestry systems"
        before = copy.deepcopy(source)
        selected = records(source)
        self.assertFalse(any(m.canonical_name.strip() == "AGROFORESTRY" for m in selected))
        self.assertTrue(any(m.canonical_name == "Agroforestry systems" for m in selected))
        self.assertEqual(source, before)


if __name__ == "__main__":
    unittest.main()
