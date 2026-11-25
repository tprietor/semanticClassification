import os
import random
import sys
import threading
import time
import types
import unittest
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import UUID

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

if "src.services.pdf_converter" not in sys.modules:
    pdf_converter_stub = types.ModuleType("src.services.pdf_converter")
    pdf_converter_stub.PdfConverter = type("PdfConverter", (), {})
    sys.modules["src.services.pdf_converter"] = pdf_converter_stub

import networkx as nx
from pydantic import ValidationError

from src.analysis.cooccurrence import MentionRecord, load_db_mentions
from src.categories import ACTIVE_CATEGORIES
from src.controlled_vocabulary import is_saf_entity_name
from src.analysis.explorer import (
    DEFAULT_EXCLUDED_ENTITY_NAMES,
    DEFAULT_EXCLUDED_ENTITY_NAMES_BY_CATEGORY,
    PERIODS,
    ExplorerFilterError,
    ExplorerFilters,
    build_explorer_network,
    build_ranked_network,
    compare_rankings,
    compute_node_metrics,
    entity_exclusion_key,
    exclude_entities,
    resolve_category_pairs,
    select_shown_network,
)
from src.api.main import app
from src.api.routers.explorer import _filters, _scope, explorer_network
from src.api.schemas.explorer import (
    ExplorerCompareRequest,
    ExplorerCompareResponse,
    ExplorerNetworkRequest,
    ExplorerNetworkResponse,
)
from src.services.explorer import (
    _RANKED_NETWORKS,
    ExplorerFiltroInvalido,
    ExplorerScope,
    ExplorerService,
    RankedNetworkCache,
    _data_fingerprint,
    _scoped_documents,
)

DOC_A = "00000000-0000-0000-0000-00000000000a"
DOC_B = "00000000-0000-0000-0000-00000000000b"
DOC_C = "00000000-0000-0000-0000-00000000000c"

ENTITIES = {
    "coop": ("cooperativa", "CHAR"),
    "minero": ("minero", "CHAR"),
    "podas": ("podas", "PRAC"),
    "vivero": ("vivero", "soft_INFRA"),
    "plan": ("plan de manejo", "RUL"),
    "rio": ("río Tambopata", "LOC"),
    "carretera": ("carretera", "INFRA"),
}


def _sentences(*sentences: tuple[str, str, tuple[str, ...]]) -> list[MentionRecord]:
    """Crea menciones a partir de (documento, oración, entidades)."""

    mentions = []
    for document_id, sentence_id, entity_keys in sentences:
        for offset, key in enumerate(entity_keys):
            name, category = ENTITIES[key]
            mentions.append(
                MentionRecord(
                    document_id=document_id,
                    sentence_id=sentence_id,
                    canonical_id=key,
                    canonical_name=name,
                    category=category,
                    text=name,
                    start=offset * 100,
                    end=offset * 100 + len(name),
                    context=f"{sentence_id} en {document_id}",
                    ambiguity="low",
                )
            )
    return mentions


CORPUS = _sentences(
    (DOC_A, "s1", ("coop", "podas", "vivero")),
    (DOC_A, "s2", ("coop", "plan")),
    (DOC_A, "s3", ("rio", "podas")),
    (DOC_B, "s1", ("coop", "podas", "plan")),
    (DOC_B, "s2", ("vivero", "rio")),
    (DOC_B, "s3", ("minero", "coop")),
    (DOC_C, "s1", ("podas", "rio")),
)


def _node_ids(network: dict) -> set[str]:
    return {node["id"] for node in network["nodes"]}


def _pairs(network: dict) -> set[str]:
    return {edge["category_pair"] for edge in network["edges"]}


class ExplorerNetworkTests(unittest.TestCase):
    def test_kas_unifies_categories_before_pair_filtering_without_merging_ids(self):
        source = [replace(CORPUS[0], canonical_id=category, canonical_name="shared name",
                          category=category, start=index * 100, end=index * 100 + 5)
                  for index, category in enumerate(("ATT", "KNOW", "SKILL"))]
        original = list(source)
        network = build_explorer_network(source, ExplorerFilters(
            categories=("KAS",), link_mode="within", minimum_node_document_count=1,
            top_n=None, excluded_entity_names=(),
        ))
        self.assertEqual(_node_ids(network), {"ATT", "KNOW", "SKILL"})
        self.assertEqual({node["category"] for node in network["nodes"]}, {"KAS"})
        self.assertEqual(_pairs(network), {"KAS--KAS"})
        self.assertEqual(len(network["edges"]), 3)
        self.assertEqual(source, original)
        self.assertEqual({m.category for m in source}, {"ATT", "KNOW", "SKILL"})
        # Las categorías originales ahora son una sola; between no puede
        # conservar enlaces entre ATT y KNOW como si siguieran separadas.
        with self.assertRaises(ExplorerFilterError):
            build_explorer_network(source, ExplorerFilters(
                categories=("ATT", "KNOW"), link_mode="between",
            ))

    def test_legacy_filters_and_pairs_select_the_whole_kas_group(self):
        body = ExplorerNetworkRequest(
            categories=["ATT", "KNOW", "SKILL", "CHAR"], link_mode="pairs",
            category_pairs=[["ATT", "CHAR"], ["KNOW", "CHAR"]],
        )
        filters = _filters(body, top_n=None)
        self.assertEqual(filters.categories, ("KAS", "CHAR"))
        self.assertEqual(filters.category_pairs, (("KAS", "CHAR"),))

    def test_default_links_eight_network_categories_and_counts_every_stage(self) -> None:
        network = build_explorer_network(
            CORPUS, ExplorerFilters(minimum_node_document_count=1, top_n=None)
        )

        self.assertIn("KAS", network["stages"]["categories"])
        self.assertFalse({"ATT", "KNOW", "SKILL"} & set(network["stages"]["categories"]))
        self.assertEqual(len(network["stages"]["categories"]), 8)
        self.assertEqual(
            _node_ids(network), {"coop", "minero", "podas", "vivero", "plan", "rio"}
        )
        self.assertEqual(network["stages"]["mentions"], len(CORPUS))
        self.assertEqual(network["stages"]["shown"]["nodes"], 6)

    def test_legacy_categories_join_only_when_present(self) -> None:
        with_legacy = CORPUS + _sentences((DOC_A, "s9", ("carretera", "podas")))

        self.assertNotIn(
            "INFRA",
            build_explorer_network(CORPUS, ExplorerFilters())["stages"]["categories"],
        )
        network = build_explorer_network(
            with_legacy, ExplorerFilters(minimum_node_document_count=1)
        )
        self.assertIn("INFRA", network["stages"]["categories"])
        self.assertIn("carretera", _node_ids(network))

    def test_link_modes_restrict_category_pairs(self) -> None:
        between = build_explorer_network(
            CORPUS,
            ExplorerFilters(
                categories=("CHAR", "PRAC"),
                link_mode="between",
                minimum_node_document_count=1,
            ),
        )
        within = build_explorer_network(
            CORPUS,
            ExplorerFilters(
                categories=("CHAR",), link_mode="within", minimum_node_document_count=1
            ),
        )
        pairs = build_explorer_network(
            CORPUS,
            ExplorerFilters(
                categories=("CHAR", "PRAC", "RUL"),
                link_mode="pairs",
                category_pairs=(("RUL", "CHAR"),),
                minimum_node_document_count=1,
            ),
        )

        self.assertEqual(_pairs(between), {"CHAR--PRAC"})
        self.assertEqual(_pairs(within), {"CHAR--CHAR"})
        self.assertEqual(_node_ids(within), {"coop", "minero"})
        self.assertEqual(_pairs(pairs), {"CHAR--RUL"})
        self.assertEqual(_node_ids(pairs), {"coop", "plan"})

    def test_invalid_link_combinations_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ExplorerFilterError, "between"):
            resolve_category_pairs(("CHAR",), "between")
        with self.assertRaisesRegex(ExplorerFilterError, "no seleccionadas"):
            resolve_category_pairs(("CHAR",), "pairs", (("CHAR", "LOC"),))
        with self.assertRaisesRegex(ExplorerFilterError, "requiere"):
            resolve_category_pairs(("CHAR",), "pairs", None)
        with self.assertRaisesRegex(ExplorerFilterError, "no permitidas"):
            build_explorer_network(CORPUS, ExplorerFilters(categories=("GOV",)))

    def test_document_recurrence_removes_single_document_entities(self) -> None:
        network = build_explorer_network(
            CORPUS, ExplorerFilters(minimum_node_document_count=2, top_n=None)
        )

        # minero solo aparece en DOC_B.
        self.assertNotIn("minero", _node_ids(network))
        self.assertEqual(network["stages"]["cooccurrence"]["nodes"], 6)
        self.assertEqual(network["stages"]["document_recurrence"]["nodes"], 5)

    def test_minimum_edge_weight_drops_weak_links_and_orphans(self) -> None:
        network = build_explorer_network(
            CORPUS,
            ExplorerFilters(
                minimum_node_document_count=1,
                edge_weighting="sentence-count",
                minimum_edge_weight=2,
                top_n=None,
            ),
        )

        self.assertTrue(all(edge["sentence_count"] >= 2 for edge in network["edges"]))
        self.assertEqual(
            {(edge["source"], edge["target"]) for edge in network["edges"]},
            {("coop", "podas"), ("coop", "plan"), ("podas", "rio")},
        )
        self.assertNotIn("minero", _node_ids(network))

    def test_metrics_are_ranked_on_full_network_before_top_n(self) -> None:
        full = build_explorer_network(
            CORPUS, ExplorerFilters(minimum_node_document_count=1, top_n=None)
        )
        top_two = build_explorer_network(
            CORPUS, ExplorerFilters(minimum_node_document_count=1, top_n=2)
        )

        full_by_id = {node["id"]: node for node in full["nodes"]}
        self.assertEqual(len(top_two["nodes"]), 2)
        self.assertEqual(
            [node["ranks"]["pagerank"] for node in top_two["nodes"]], [1, 2]
        )
        for node in top_two["nodes"]:
            self.assertEqual(node["metrics"], full_by_id[node["id"]]["metrics"])
        self.assertTrue(
            all(
                edge["source"] in _node_ids(top_two)
                and edge["target"] in _node_ids(top_two)
                for edge in top_two["edges"]
            )
        )
        self.assertTrue(
            any("Se muestran los 2" in warning for warning in top_two["warnings"])
        )

    def test_bridge_entity_has_highest_betweenness(self) -> None:
        bridge = _sentences(
            (DOC_A, "s1", ("minero", "coop")),
            (DOC_A, "s2", ("coop", "podas")),
            (DOC_A, "s3", ("podas", "rio")),
            (DOC_A, "s4", ("podas", "plan")),
        )
        network = build_explorer_network(
            bridge,
            ExplorerFilters(
                minimum_node_document_count=1,
                ranking_metric="betweenness",
                top_n=None,
            ),
        )

        self.assertEqual(network["nodes"][0]["id"], "podas")
        self.assertEqual(network["metric_provenance"]["betweenness"], "exact")

    def test_excluded_entities_are_removed_before_metrics(self) -> None:
        filters = ExplorerFilters(minimum_node_document_count=1, top_n=None)
        full = build_explorer_network(CORPUS, filters)
        without = build_explorer_network(
            CORPUS, replace(filters, excluded_entity_ids=("coop", "fantasma"))
        )

        self.assertIn("coop", _node_ids(full))
        self.assertNotIn("coop", _node_ids(without))
        coop_mentions = sum(1 for mention in CORPUS if mention.canonical_id == "coop")
        self.assertEqual(
            without["stages"]["mentions"], full["stages"]["mentions"] - coop_mentions
        )
        # Las métricas del resto se recalculan sin la entidad: alguien más es #1.
        leader = min(without["nodes"], key=lambda node: node["ranks"]["pagerank"])
        self.assertEqual(leader["ranks"]["pagerank"], 1)
        self.assertNotEqual(leader["id"], "coop")
        self.assertEqual(
            without["excluded_entities"],
            [
                {
                    "id": "coop",
                    "name": "cooperativa",
                    "category": "CHAR",
                    "mention_count": coop_mentions,
                    "partial": False,
                    "remaining_mention_count": 0,
                },
                {"id": "fantasma", "name": None, "category": None, "mention_count": 0,
                 "partial": False, "remaining_mention_count": 0},
            ],
        )
        self.assertEqual(full["excluded_entities"], [])

    def test_exclusions_are_part_of_the_cached_network(self) -> None:
        base = ExplorerFilters()
        self.assertNotEqual(
            replace(base, excluded_entity_ids=("coop",)).structural(),
            base.structural(),
        )
        self.assertNotEqual(
            replace(base, excluded_entity_names=()).structural(),
            base.structural(),
        )
        self.assertNotEqual(
            replace(base, excluded_entity_names_by_category=()).structural(),
            base.structural(),
        )
        self.assertEqual(
            hash(base.structural()), hash(replace(base, top_n=10).structural())
        )

    def test_loc_exclusions_preserve_other_categories_and_run_before_metrics(self):
        names = dict(DEFAULT_EXCLUDED_ENTITY_NAMES_BY_CATEGORY)["LOC"]
        mentions = [MentionRecord(
            document_id=DOC_A, sentence_id="s1", canonical_id=f"{category}-{index}",
            canonical_name=name, category=category, text=name.upper(),
            start=0, end=len(name), context="Evidence", ambiguity="low",
        ) for category in ("LOC", "eco_INFRA") for index, name in enumerate(names)]
        original = list(mentions)
        filters = ExplorerFilters(minimum_node_document_count=1, top_n=None)
        actual = build_explorer_network(mentions, filters)
        expected = build_explorer_network(
            [m for m in mentions if m.category != "LOC"],
            replace(filters, excluded_entity_names_by_category=()),
        )
        self.assertEqual(actual["nodes"], expected["nodes"])
        self.assertEqual(actual["edges"], expected["edges"])
        self.assertEqual(actual["stages"], expected["stages"])
        self.assertEqual(len(actual["excluded_entities"]), len(names))
        self.assertTrue(all(e["category"] == "LOC" for e in actual["excluded_entities"]))
        self.assertEqual(mentions, original)

    def test_scoped_exclusions_match_literal_aliases_without_category_spill(self):
        def mention(identifier, name, text, category="LOC"):
            return MentionRecord(
                document_id=DOC_A, sentence_id="s1", canonical_id=identifier,
                canonical_name=name, category=category, text=text, start=0,
                end=len(text), context="Evidence", ambiguity="low",
            )
        mentions = [
            mention("forests", "Amazonian forests", "Amazonian forest"),
            mention("forests", "Amazonian forests", "Amazonian forest", "eco_INFRA"),
            mention("alias", "Another place", "P.E.M."),
            mention("alias", "Another place", "Allowed place"),
            mention("route", "Puerto Maldonado – Iñapari", "Puerto Maldonado-Iñapari"),
            mention("river", "Madre de Dios River", "MADRE DE DIOS RIVER"),
            mention("keep", "Tambopata National Reserve", "Tambopata National Reserve"),
            mention("area", "Área", "ÁREA"),
        ]
        kept, excluded = exclude_entities(
            mentions, (), (), DEFAULT_EXCLUDED_ENTITY_NAMES_BY_CATEGORY
        )
        self.assertEqual(kept, [mentions[1], mentions[3], mentions[6]])
        by_id = {e["id"]: e for e in excluded}
        self.assertTrue(by_id["alias"]["partial"])
        self.assertEqual(by_id["alias"]["remaining_mention_count"], 1)
        self.assertTrue(by_id["forests"]["partial"])
        self.assertEqual(exclude_entities(mentions, (), (), ()), (mentions, ()))

    def test_land_and_forest_exclude_whole_names_in_all_categories_only(self):
        excluded_forms = ("land", "LAND", "lands", "forest", "Forest", "forests")
        compounds = ("land use", "forest management", "forest resources", "woodland", "landscape")
        for category in sorted(ACTIVE_CATEGORIES):
            with self.subTest(category=category):
                mentions = [MentionRecord(
                    document_id=DOC_A, sentence_id="s1", canonical_id=str(index),
                    canonical_name=name, category=category, text=name,
                    start=0, end=len(name), context="Evidence", ambiguity="low",
                ) for index, name in enumerate((*excluded_forms, *compounds))]
                kept, excluded = exclude_entities(mentions, (), DEFAULT_EXCLUDED_ENTITY_NAMES)
                self.assertEqual([m.text for m in kept], list(compounds))
                self.assertEqual(sum(e["mention_count"] for e in excluded), len(excluded_forms))

    def test_default_name_exclusions_match_all_ids_before_building_metrics(self) -> None:
        with patch.dict(
            ENTITIES,
            {
                "madre": ("Madre de Dios", "LOC"),
                "madre_other": (" MADRE  DE DIOS ", "CHAR"),
                "agro": ("Agroforestry", "PRAC"),
                "agro_other": ("AGROFORESTRY", "LOC"),
                "systems": ("Agroforestry systems", "PRAC"),
            },
        ):
            mentions = _sentences(
                (DOC_A, "s1", ("coop", "madre", "agro", "systems", "rio")),
                (DOC_B, "s1", ("coop", "madre_other", "agro_other", "systems", "rio")),
            )
        filters = ExplorerFilters(minimum_node_document_count=1, top_n=None)
        network = build_explorer_network(mentions, filters)
        expected = build_explorer_network(
            mentions,
            replace(
                filters,
                excluded_entity_names=(),
                excluded_entity_ids=("agro", "agro_other", "madre", "madre_other", "systems"),
            ),
        )

        self.assertEqual(network, expected)
        self.assertEqual(_node_ids(network), {"coop", "rio"})
        self.assertEqual(network["stages"]["mentions"], len(mentions) - 6)
        self.assertEqual(
            {entity["id"] for entity in network["excluded_entities"]},
            {"agro", "agro_other", "madre", "madre_other", "systems"},
        )
        restored = build_explorer_network(
            mentions, replace(filters, excluded_entity_names=())
        )
        self.assertEqual(len(_node_ids(restored)), 7)

    def test_name_exclusions_combine_with_ids_and_report_each_entity_once(self) -> None:
        network = build_explorer_network(
            CORPUS,
            ExplorerFilters(
                minimum_node_document_count=1,
                top_n=None,
                excluded_entity_ids=("coop", "fantasma"),
                excluded_entity_names=(" COOPERATIVA ", "Podas"),
            ),
        )

        self.assertFalse({"coop", "podas"} & _node_ids(network))
        self.assertEqual(
            [entity["id"] for entity in network["excluded_entities"]],
            ["coop", "fantasma", "podas"],
        )
        self.assertEqual(
            network["excluded_entities"][0]["mention_count"],
            sum(mention.canonical_id == "coop" for mention in CORPUS),
        )

    def test_literal_exclusions_survive_alias_canonicalization_and_future_documents(self):
        mentions = [
            MentionRecord(document_id=doc, sentence_id="s1", canonical_id="systems", canonical_name="sistemas agroflorestais",
                          category="PRAC", text=text, start=0, end=len(text), context="Evidence", ambiguity="low")
            for doc, text in ((DOC_A, "SAF"), (DOC_B, "SAFs"), (DOC_C, "Forest production systems"))
        ]
        original = list(mentions)
        kept, excluded = exclude_entities(mentions, (), DEFAULT_EXCLUDED_ENTITY_NAMES)
        self.assertEqual([m.text for m in kept], ["Forest production systems"])
        self.assertEqual(excluded[0]["mention_count"], 2)
        self.assertTrue(excluded[0]["partial"])
        self.assertEqual(excluded[0]["remaining_mention_count"], 1)
        self.assertEqual(mentions, original)
        self.assertEqual(exclude_entities(mentions, (), ()), (mentions, ()))
        kept, excluded = exclude_entities(mentions, ("systems",), ())
        self.assertEqual(kept, [])
        self.assertEqual(excluded[0]["mention_count"], 3)
        self.assertFalse(excluded[0]["partial"])

    def test_entire_saf_family_is_excluded_in_all_categories_and_new_documents(self):
        for category in sorted(ACTIVE_CATEGORIES):
            with self.subTest(category=category):
                mentions = [MentionRecord(
                    document_id=DOC_C, sentence_id="new-s1", canonical_id="translated-system", canonical_name="sistemas agroflorestais",
                    category=category, text=text, start=0, end=len(text), context="Evidence", ambiguity="low",
                ) for text in ("SAFs-A", "SAFs-F", "SAF-Dendê", "SAF 14", "SAF type IV", "SAFs-X", "SAF implementation")]
                kept, excluded = exclude_entities(mentions, (), DEFAULT_EXCLUDED_ENTITY_NAMES)
                self.assertEqual(kept, [])
                self.assertEqual(excluded[0]["mention_count"], len(mentions))
                self.assertFalse(excluded[0]["partial"])
                self.assertEqual(exclude_entities(mentions, (), ()), (mentions, ()))

    def test_saf_family_does_not_match_other_words(self):
        for text in ("SAFA", "SAFTA", "SAFTA farmers", "safe drinking water", "safety", "safeguards"):
            with self.subTest(text=text):
                self.assertFalse(is_saf_entity_name(text))
        for text in ("SAFs-A", "SAFsA", "SAFsF", "S.A.F.s-F", "SAF-dendê", "SAF type II", "new SAFs-B variant"):
            with self.subTest(text=text):
                self.assertTrue(is_saf_entity_name(text))

    def test_literal_exclusions_run_before_cooccurrence_and_metrics(self):
        mentions = _sentences((DOC_A, "s1", ("coop", "podas")), (DOC_B, "s2", ("coop", "podas")))
        # Same preferred name, but one source mention is an explicitly excluded alias.
        mentions[0] = replace(mentions[0], text="farmers")
        actual = build_explorer_network(mentions, ExplorerFilters(minimum_node_document_count=1, top_n=None))
        expected = build_explorer_network(mentions[1:], ExplorerFilters(minimum_node_document_count=1, top_n=None))
        self.assertEqual(actual["nodes"], expected["nodes"])
        self.assertEqual(actual["edges"], expected["edges"])
        self.assertEqual(actual["stages"], expected["stages"])

    def test_editorial_exclusions_apply_to_all_categories_without_mutating_mentions(self):
        mentions = [
            MentionRecord(
                document_id=DOC_A, sentence_id="s1", canonical_id=f"{category}-{index}",
                canonical_name=name, category=category, text=name, start=0, end=len(name),
                context="Evidence", ambiguity="low",
            )
            for category in sorted(ACTIVE_CATEGORIES)
            for index, name in enumerate(DEFAULT_EXCLUDED_ENTITY_NAMES)
        ]
        original = list(mentions)
        kept, excluded = exclude_entities(mentions, (), DEFAULT_EXCLUDED_ENTITY_NAMES)
        self.assertEqual(kept, [])
        self.assertEqual(len(excluded), len(mentions))
        self.assertEqual({row["category"] for row in excluded}, ACTIVE_CATEGORIES)
        self.assertTrue(all(row["mention_count"] == 1 for row in excluded))
        self.assertEqual(mentions, original)

    def test_editorial_exclusions_cover_format_and_noun_variants(self):
        keys = {entity_exclusion_key(name) for name in DEFAULT_EXCLUDED_ENTITY_NAMES}
        for name in (
            " AGROFORESTRY ", "S.A.F.", "s.a.f.s.", "A.F.S.s", "Peru", "PERÚ.",
            "Regio\u0301n MADRE de DIOS", "RIO MADRE-DE-DIOS", "Small-scale farmers",
            "small scale farmer", "smallholder farmers.", "farmers’ co-operative",
            "farmer's cooperatives.", "farmers’ associations", "NON—PROFIT ORGANIZATIONS",
            "non profit organization", "ACTOR GROUP", "academic institutions",
            "on site partner", "36 SITE", "agroforestry management sites",
            "local agroforestry NGO", "MID SCALE FARMER", "non-protected area", "NGO’s",
            "Amazon / Amazon Region", "plot", "Plot", "PLOT.", "plots", "PLOTS", "plot’s",
            "pilot plots", "Pilot plot", "PLOTS 5 AND 6", "ROAD CONSTRUCTION.",
            "Leticia-Tarapaca road", "Leticia–Tarapaca Road", "NEW ROAD", "ROADS.",
            "Transamazonica Road Region", "new roads", "NEW ROADS.",
            "the Amazon", "THE AMAZON.", "Amazonia", "Amazônia", "AMAZONÍA", "Peruvian Amazon",
            "Agroforestry Systems", "AGROFORESTRY SYSTEMS.", "agroforestry system",
            "Agroforestry Practices?", "AGRICULTURAL PRACTICES.",
            "SAFT", "Agroforest", "Agroforests", "Agroforestry Production System.",
            "SAFTA", "AFSs-F", "AFSs-A", "AFSs-F-based economy", "creating and managing AFSs",
            "AFSs-A variant", "AFSsF", "AFSs–F variant", "Agroforestry systems (AFSs)",
            "State", "state", "STATE", "State.",
        ):
            with self.subTest(name=name):
                self.assertIn(entity_exclusion_key(name), keys)

    def test_editorial_exclusions_do_not_match_substrings_or_invent_municipalities(self):
        keys = {entity_exclusion_key(name) for name in DEFAULT_EXCLUDED_ENTITY_NAMES}
        for name in (
            "Agroforestry systems research", "río Tambopata", "farmer training",
            "cacao farmer training", "association of seed producers",
            "agroforestry practice", "indigenous agroforestry practices", "traditional agricultural practices",
            "SAFTA certification", "cacao agroforest", "agroforestry production system adoption",
            "Peruvian government", "Amazonian biodiversity",
            "Proyecto Especial Madre de Dios research team", "Puerto Maldonado",
            "agroforestry plots", "demonstration plots", "research plots",
            "Plot design", "Plot preparation", "Field", "chacras",
            "road", "road networks", "road access", "road building",
            "rural roads", "logging roads", "railroads", "road construction training",
            "Peruvian Amazon research team", "Amazonian biodiversity research",
            "the State", "state law", "Amazonas state", "State entities", "states",
        ):
            with self.subTest(name=name):
                self.assertNotIn(entity_exclusion_key(name), keys)

    def test_empty_results_return_warnings_instead_of_errors(self) -> None:
        no_mentions = build_explorer_network([], ExplorerFilters())
        too_strict = build_explorer_network(
            CORPUS, ExplorerFilters(minimum_node_document_count=10)
        )

        self.assertEqual(no_mentions["nodes"], [])
        self.assertTrue(no_mentions["warnings"])
        self.assertEqual(too_strict["edges"], [])
        self.assertIn("minimum_node_document_count", too_strict["warnings"][0])


def _weighted_graph(
    node_count: int, edge_count: int, seed: int, components: int = 1
) -> nx.Graph:
    """Red aleatoria con pesos analíticos, opcionalmente en varias componentes."""

    rng = random.Random(seed)
    graph = nx.Graph()
    per_component = node_count // components
    for component in range(components):
        offset = component * per_component
        nodes = [f"n{offset + index}" for index in range(per_component)]
        graph.add_nodes_from(nodes, document_count=1)
        for index in range(1, len(nodes)):
            graph.add_edge(nodes[index], nodes[rng.randrange(index)])
        while graph.number_of_edges() < edge_count * (component + 1) // components:
            source, target = rng.sample(nodes, 2)
            graph.add_edge(source, target)
    for source, target in graph.edges():
        # Pesos de la forma k/4, como los de ponderación fraccional, para que
        # aparezcan caminos mínimos empatados.
        graph[source][target]["analysis_weight"] = rng.randint(1, 12) / 4
    return graph


def _reference_metrics(graph: nx.Graph) -> dict[str, dict[str, float]]:
    """Métricas de networkx con distancias racionales exactas.

    Con distancias en coma flotante, networkx no reconoce algunos caminos
    mínimos empatados (4/3 + 4/6 no suma exactamente 2) y su intermediación se
    desvía hasta 2e-4. Con fracciones los empates son exactos: es la referencia
    correcta, y la que igraph reproduce.
    """

    distance_graph = nx.Graph()
    distance_graph.add_nodes_from(graph)
    for source, target, attributes in graph.edges(data=True):
        weight = Fraction(attributes["analysis_weight"]).limit_denominator(1000)
        distance_graph.add_edge(source, target, distance=1 / weight)
    closeness = nx.closeness_centrality(distance_graph, distance="distance")
    betweenness = nx.betweenness_centrality(
        distance_graph, weight="distance", normalized=True
    )
    return {
        node: {
            "closeness": float(closeness[node]),
            "betweenness": float(betweenness[node]),
        }
        for node in graph
    }


class NodeMetricsTests(unittest.TestCase):
    def assert_matches_networkx(self, graph: nx.Graph) -> None:
        metrics, provenance = compute_node_metrics(graph)
        reference = _reference_metrics(graph)

        self.assertEqual(provenance["betweenness"], "exact")
        self.assertEqual(set(metrics), set(graph))
        for node in graph:
            for metric in ("closeness", "betweenness"):
                with self.subTest(node=node, metric=metric):
                    self.assertAlmostEqual(
                        metrics[node][metric], reference[node][metric], places=10
                    )

    def test_connected_network_matches_networkx(self) -> None:
        self.assert_matches_networkx(_weighted_graph(120, 400, seed=1))

    def test_disconnected_network_matches_networkx(self) -> None:
        graph = _weighted_graph(150, 300, seed=2, components=3)
        self.assertEqual(nx.number_connected_components(graph), 3)
        self.assert_matches_networkx(graph)

    def test_small_networks_match_networkx(self) -> None:
        for edges in ([("a", "b")], [("a", "b"), ("b", "c")], [("a", "b"), ("c", "d")]):
            graph = nx.Graph()
            for source, target in edges:
                graph.add_edge(source, target, analysis_weight=0.5)
            nx.set_node_attributes(graph, 1, "document_count")
            with self.subTest(edges=edges):
                self.assert_matches_networkx(graph)

    def test_large_network_is_exact_and_interactive(self) -> None:
        # Con networkx puro, cercanía e intermediación de esta red tardaban
        # unos 40 s; con igraph, menos de 2 s. El límite es holgado para no
        # fallar en máquinas lentas.
        graph = _weighted_graph(1500, 7500, seed=3)

        started = time.perf_counter()
        metrics, provenance = compute_node_metrics(graph)
        elapsed = time.perf_counter() - started

        self.assertEqual(
            provenance, {"betweenness": "exact", "betweenness_sample_size": None}
        )
        self.assertEqual(len(metrics), 1500)
        self.assertLess(elapsed, 10)


class SelectShownNetworkTests(unittest.TestCase):
    FILTERS = ExplorerFilters(minimum_node_document_count=1)

    def test_selection_from_ranked_network_equals_full_build(self) -> None:
        ranked = build_ranked_network(CORPUS, self.FILTERS.structural())

        for metric in ("pagerank", "betweenness", "document_count"):
            for top_n in (None, 1, 3, 100):
                with self.subTest(metric=metric, top_n=top_n):
                    expected = build_explorer_network(
                        CORPUS,
                        ExplorerFilters(
                            minimum_node_document_count=1,
                            ranking_metric=metric,
                            top_n=top_n,
                        ),
                    )
                    self.assertEqual(
                        select_shown_network(ranked, metric, top_n), expected
                    )

    def test_structural_filters_ignore_only_selection_fields(self) -> None:
        base = ExplorerFilters(categories=("CHAR", "PRAC"), minimum_edge_weight=0.5)

        self.assertEqual(
            replace(base, ranking_metric="degree", top_n=10).structural(),
            base.structural(),
        )
        self.assertNotEqual(
            replace(base, minimum_node_document_count=3).structural(),
            base.structural(),
        )

    def test_modifying_a_response_does_not_alter_the_ranked_network(self) -> None:
        ranked = build_ranked_network(CORPUS, self.FILTERS.structural())
        first = select_shown_network(ranked, "pagerank", 2)

        first["warnings"].insert(0, "aviso del servicio")
        first["stages"]["cooccurrence"]["nodes"] = -1
        first["nodes"][0]["metrics"]["pagerank"] = -1.0

        second = select_shown_network(ranked, "pagerank", 2)
        self.assertNotIn("aviso del servicio", second["warnings"])
        self.assertGreater(second["stages"]["cooccurrence"]["nodes"], 0)
        self.assertGreater(second["nodes"][0]["metrics"]["pagerank"], 0)

    def test_unknown_ranking_metric_is_rejected(self) -> None:
        ranked = build_ranked_network(CORPUS, self.FILTERS.structural())

        with self.assertRaises(ExplorerFilterError):
            select_shown_network(ranked, "eigenvector", None)


class RankedNetworkCacheTests(unittest.TestCase):
    def test_reuses_value_until_it_expires(self) -> None:
        now = [0.0]
        cache = RankedNetworkCache(max_entries=4, ttl_seconds=10, clock=lambda: now[0])
        build = Mock(side_effect=["v1", "v2"])

        self.assertEqual(cache.get_or_build("k", build), "v1")
        now[0] = 9.9
        self.assertEqual(cache.get_or_build("k", build), "v1")
        now[0] = 10.0
        self.assertEqual(cache.get_or_build("k", build), "v2")
        self.assertEqual(build.call_count, 2)

    def test_evicts_least_recently_used_entry(self) -> None:
        cache = RankedNetworkCache(max_entries=2, ttl_seconds=60)
        cache.get_or_build("a", lambda: "a")
        cache.get_or_build("b", lambda: "b")
        cache.get_or_build("a", lambda: "nuevo a")
        cache.get_or_build("c", lambda: "c")

        self.assertEqual(len(cache), 2)
        self.assertEqual(cache.get_or_build("a", lambda: "nuevo a"), "a")
        self.assertEqual(cache.get_or_build("b", lambda: "nuevo b"), "nuevo b")

    def test_edge_budget_evicts_old_networks_but_keeps_the_newest(self) -> None:
        def network(edges: int) -> SimpleNamespace:
            return SimpleNamespace(graph=nx.path_graph(edges + 1))

        cache = RankedNetworkCache(max_entries=10, ttl_seconds=60, max_edges=100)
        first = cache.get_or_build("a", lambda: network(40))
        cache.get_or_build("b", lambda: network(40))
        self.assertEqual(len(cache), 2)

        # 120 links superan el presupuesto: sale "a", la usada hace más tiempo.
        cache.get_or_build("c", lambda: network(40))
        self.assertEqual(len(cache), 2)
        self.assertIsNot(cache.get_or_build("a", lambda: network(40)), first)

        # Una red más grande que el presupuesto se conserva sola.
        huge = cache.get_or_build("d", lambda: network(500))
        self.assertEqual(len(cache), 1)
        self.assertIs(cache.get_or_build("d", lambda: network(500)), huge)

    def test_errors_are_not_cached(self) -> None:
        cache = RankedNetworkCache(max_entries=2, ttl_seconds=60)

        with self.assertRaises(ExplorerFilterError):
            cache.get_or_build("k", Mock(side_effect=ExplorerFilterError("x")))
        self.assertEqual(len(cache), 0)
        self.assertEqual(cache.get_or_build("k", lambda: "ok"), "ok")

    def test_concurrent_requests_build_once(self) -> None:
        cache = RankedNetworkCache(max_entries=2, ttl_seconds=60)
        calls = []

        def slow_build():
            calls.append(threading.get_ident())
            time.sleep(0.2)
            return "red"

        results = []
        threads = [
            threading.Thread(
                target=lambda: results.append(cache.get_or_build("k", slow_build))
            )
            for _ in range(5)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(results, ["red"] * 5)
        self.assertEqual(len(calls), 1)


class CompareRankingsTests(unittest.TestCase):
    def test_reports_central_node_change_and_top_k_movement(self) -> None:
        early = build_explorer_network(
            _sentences(
                (DOC_A, "s1", ("coop", "podas")),
                (DOC_A, "s2", ("coop", "plan")),
                (DOC_A, "s3", ("coop", "rio")),
            ),
            ExplorerFilters(
                minimum_node_document_count=1, ranking_metric="degree", top_n=None
            ),
        )
        late = build_explorer_network(
            _sentences(
                (DOC_B, "s1", ("vivero", "podas")),
                (DOC_B, "s2", ("vivero", "plan")),
                (DOC_B, "s3", ("vivero", "rio")),
                (DOC_B, "s4", ("vivero", "minero")),
            ),
            ExplorerFilters(
                minimum_node_document_count=1, ranking_metric="degree", top_n=None
            ),
        )

        comparison = compare_rankings(
            {"2021-2023": early, "2024-2026": late}, metric="degree", top_k=1
        )

        self.assertEqual(
            comparison["central_by_period"]["2021-2023"]["degree"]["id"], "coop"
        )
        self.assertEqual(
            comparison["central_by_period"]["2024-2026"]["degree"]["id"], "vivero"
        )
        change = comparison["changes"][0]
        self.assertEqual([item["id"] for item in change["entered"]], ["vivero"])
        self.assertEqual([item["id"] for item in change["left"]], ["coop"])
        coop = next(item for item in comparison["trajectories"] if item["id"] == "coop")
        self.assertEqual(coop["points"][0]["rank"], 1)
        self.assertIsNone(coop["points"][1]["rank"])


class ExplorerServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        _RANKED_NETWORKS.clear()
        self.addCleanup(_RANKED_NETWORKS.clear)
        fingerprint = patch(
            "src.services.explorer._data_fingerprint", return_value=(7, 5, "t1")
        )
        self.fingerprint = fingerprint.start()
        self.addCleanup(fingerprint.stop)

    @staticmethod
    def _document(document_id: str, year: int | None) -> SimpleNamespace:
        return SimpleNamespace(
            id=UUID(document_id),
            original_filename=f"{document_id[-1]}.pdf",
            year=year,
            incubator_number=1,
            language="es",
            document_type="technical_report",
        )

    def test_scope_defaults_to_agroforestry_and_all_disables_the_filter(self) -> None:
        self.assertEqual(ExplorerScope().productive_sector, "Agroforestry")
        self.assertEqual(
            _scope(ExplorerNetworkRequest()).productive_sector, "Agroforestry"
        )
        self.assertIsNone(
            _scope(ExplorerNetworkRequest(productive_sector="all")).productive_sector
        )
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(productive_sector="Mining")

    def test_scoped_documents_query_filters_by_sector_only_when_requested(self) -> None:
        def compiled_where(scope: ExplorerScope) -> str:
            db = Mock()
            db.execute.return_value.all.return_value = []
            _scoped_documents(db, scope)
            statement = db.execute.call_args.args[0]
            return str(statement.whereclause)

        self.assertIn("productive_sector", compiled_where(ExplorerScope()))
        self.assertNotIn(
            "productive_sector", compiled_where(ExplorerScope(productive_sector=None))
        )

    def test_periods_are_chronological_and_include_2000_2020(self) -> None:
        self.assertEqual(
            [period["id"] for period in PERIODS],
            ["2000-2020", "2021-2023", "2024-2026"],
        )
        self.assertEqual(ExplorerCompareRequest().periods, [p["id"] for p in PERIODS])
        self.assertEqual(ExplorerNetworkRequest(period="2000-2020").period, "2000-2020")

        db = Mock()
        db.execute.return_value.all.return_value = []
        _scoped_documents(db, ExplorerScope(period="2000-2020"))
        where = db.execute.call_args.args[0].whereclause.compile(
            compile_kwargs={"literal_binds": True}
        )
        self.assertIn("BETWEEN 2000 AND 2020", str(where))

    @staticmethod
    def _where(scope: ExplorerScope) -> str:
        db = Mock()
        db.execute.return_value.all.return_value = []
        _scoped_documents(db, scope)
        return str(
            db.execute.call_args.args[0].whereclause.compile(
                compile_kwargs={"literal_binds": True}
            )
        )

    def test_document_type_filter_selects_some_types_or_all_but_some(self) -> None:
        self.assertNotIn("document_type", self._where(ExplorerScope()))
        self.assertIn(
            "documents.document_type IN ('Other', 'WA SAM Hub')",
            self._where(ExplorerScope(document_types=("Other", "WA SAM Hub"))),
        )
        excluded = self._where(
            ExplorerScope(document_types=("WA SAM Hub",), document_type_mode="exclude")
        )
        # Excluir tipos conserva los documentos sin tipo.
        self.assertIn("documents.document_type IS NULL", excluded)
        self.assertIn("documents.document_type NOT IN ('WA SAM Hub')", excluded)

    def test_document_type_and_language_filters_combine(self) -> None:
        where = self._where(
            ExplorerScope(
                language="en", document_types=("Other",), document_type_mode="exclude"
            )
        )
        self.assertIn("documents.language = 'en'", where)
        self.assertIn("documents.document_type NOT IN ('Other')", where)

    def test_request_maps_document_types_to_the_scope(self) -> None:
        default = _scope(ExplorerNetworkRequest())
        self.assertIsNone(default.document_types)
        self.assertEqual(default.document_type_mode, "only")
        scope = _scope(
            ExplorerNetworkRequest(
                language="es",
                document_types=["WA SAM Hub", "Other", "WA SAM Hub"],
                document_type_mode="exclude",
            )
        )
        self.assertEqual(
            (scope.language, scope.document_types, scope.document_type_mode),
            ("es", ("Other", "WA SAM Hub"), "exclude"),
        )
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(document_type_mode="except")
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(document_types=[])
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(document_types=[""])

    def test_legacy_single_document_type_is_still_accepted(self) -> None:
        # El frontend anterior envía document_type; se suma a la lista.
        scope = _scope(ExplorerNetworkRequest(document_type="SERFOR"))
        self.assertEqual(scope.document_types, ("SERFOR",))
        legacy_none = _scope(ExplorerNetworkRequest(document_type=None))
        self.assertIsNone(legacy_none.document_types)

    def test_network_reports_the_document_types_in_its_scope(self) -> None:
        with (
            patch(
                "src.services.explorer._scoped_documents",
                return_value=[self._document(DOC_A, 2022)],
            ),
            patch("src.services.explorer.load_db_mentions", return_value=CORPUS),
        ):
            payload = ExplorerService.network(
                Mock(),
                ExplorerScope(document_types=("technical_report",)),
                ExplorerFilters(),
            )

        self.assertEqual(payload["scope"]["document_types"], ["technical_report"])
        self.assertEqual(payload["scope"]["document_type_mode"], "only")
        ExplorerNetworkResponse.model_validate(payload)

    def test_evidence_preserves_original_category_after_editorial_canonicalization(self):
        db = Mock()
        db.execute.return_value.all.return_value = [SimpleNamespace(
            document_id=UUID(DOC_A), sentence_id="s-road", sentence_text="Evidence of road building",
            canonical_id=UUID(DOC_B), canonical_name="road pavement", category="physical_INFRA",
            resolution_details={"source_category": "PRAC"}, mention_text="road building",
        )]
        with patch("src.services.explorer._scoped_documents", return_value=[self._document(DOC_A, 2022)]):
            payload = ExplorerService.evidence(db, DOC_B, DOC_C, ExplorerScope())
        entity = payload["items"][0]["entities"][0]
        self.assertEqual(entity["name"], "road pavement")
        self.assertEqual(entity["category"], "physical_INFRA")
        self.assertEqual(entity["source_category"], "PRAC")
        self.assertEqual(entity["mention_text"], "road building")

    def test_meta_lists_document_types_by_document_count(self) -> None:
        documents = [
            SimpleNamespace(
                **vars(self._document(document_id, 2022)),
                productive_sector="Agroforestry",
            )
            for document_id in (DOC_A, DOC_B, DOC_C)
        ]
        documents[0].document_type = "WA SAM Hub"
        documents[2].document_type = None
        db = Mock()
        db.execute.return_value.all.return_value = []
        with patch(
            "src.services.explorer._scoped_documents", return_value=documents
        ):
            payload = ExplorerService.meta(db)

        self.assertEqual(
            payload["document_types"],
            [
                {"name": "WA SAM Hub", "document_count": 1},
                {"name": "technical_report", "document_count": 1},
            ],
        )

    def test_meta_exposes_only_kas_for_the_three_source_categories(self):
        db = Mock()
        db.execute.return_value.all.return_value = [("KAS", 120), ("CHAR", 42)]
        with patch("src.services.explorer._scoped_documents", return_value=[]):
            payload = ExplorerService.meta(db)
        codes = {row["code"] for row in payload["categories"]}
        self.assertEqual(len(codes), 8)
        self.assertFalse(codes & {"ATT", "KNOW", "SKILL"})
        kas = next(row for row in payload["categories"] if row["code"] == "KAS")
        self.assertEqual(kas["entity_count"], 120)
        # Comprobar que el conteo se agrupa en SQL por la categoría transformada.
        statement = str(db.execute.call_args.args[0])
        self.assertIn("GROUP BY CASE", statement)
        self.assertIn("count(distinct", statement.lower())

    def test_unknown_period_is_rejected(self) -> None:
        with self.assertRaises(ExplorerFiltroInvalido):
            ExplorerService.network(
                Mock(), ExplorerScope(period="1999-2000"), ExplorerFilters()
            )

    def test_network_loads_mentions_only_for_scoped_documents(self) -> None:
        documents = [self._document(DOC_A, 2022), self._document(DOC_B, 2023)]
        with (
            patch("src.services.explorer._scoped_documents", return_value=documents),
            patch(
                "src.services.explorer.load_db_mentions", return_value=CORPUS
            ) as load,
        ):
            payload = ExplorerService.network(
                Mock(), ExplorerScope(period="2021-2023"), ExplorerFilters()
            )

        self.assertEqual(load.call_args.kwargs["document_ids"], [DOC_A, DOC_B])
        self.assertEqual(payload["scope"]["period"], "2021-2023")
        self.assertEqual(payload["scope"]["document_count"], 2)
        self.assertEqual(payload["version"], "entity-explorer-v1-kas-scoped-exclusions")
        ExplorerNetworkResponse.model_validate(payload)

    def test_single_document_scope_shows_network_with_default_recurrence(self) -> None:
        mentions = [item for item in CORPUS if item.document_id == DOC_A]
        with (
            patch(
                "src.services.explorer._scoped_documents",
                return_value=[self._document(DOC_A, 2022)],
            ),
            patch("src.services.explorer.load_db_mentions", return_value=mentions),
        ):
            payload = ExplorerService.network(
                Mock(), ExplorerScope(language="pt"), ExplorerFilters()
            )

        self.assertEqual(payload["scope"]["document_count"], 1)
        self.assertEqual(payload["filters"]["minimum_node_document_count"], 1)
        self.assertGreater(payload["stages"]["shown"]["nodes"], 0)
        self.assertIn("se ajustó a 1", payload["warnings"][0])
        ExplorerNetworkResponse.model_validate(payload)

    def test_single_document_respects_stricter_recurrence(self) -> None:
        mentions = [item for item in CORPUS if item.document_id == DOC_A]
        with (
            patch(
                "src.services.explorer._scoped_documents",
                return_value=[self._document(DOC_A, 2022)],
            ),
            patch("src.services.explorer.load_db_mentions", return_value=mentions),
        ):
            payload = ExplorerService.network(
                Mock(), ExplorerScope(language="pt"),
                ExplorerFilters(minimum_node_document_count=3),
            )

        self.assertEqual(payload["filters"]["minimum_node_document_count"], 3)
        self.assertEqual(payload["stages"]["shown"]["nodes"], 0)

    def test_network_without_documents_skips_database_mentions(self) -> None:
        with (
            patch("src.services.explorer._scoped_documents", return_value=[]),
            patch("src.services.explorer.load_db_mentions") as load,
        ):
            payload = ExplorerService.network(
                Mock(), ExplorerScope(), ExplorerFilters()
            )

        load.assert_not_called()
        self.assertEqual(payload["nodes"], [])
        self.assertIn("No hay documentos listos", payload["warnings"][0])

    def test_selection_changes_reuse_the_cached_network(self) -> None:
        documents = [self._document(DOC_A, 2022), self._document(DOC_B, 2023)]
        with (
            patch("src.services.explorer._scoped_documents", return_value=documents),
            patch(
                "src.services.explorer.load_db_mentions", return_value=CORPUS
            ) as load,
        ):
            first = ExplorerService.network(
                Mock(), ExplorerScope(), ExplorerFilters(minimum_node_document_count=1)
            )
            smaller = ExplorerService.network(
                Mock(),
                ExplorerScope(),
                ExplorerFilters(
                    minimum_node_document_count=1, ranking_metric="degree", top_n=2
                ),
            )
            stricter = ExplorerService.network(
                Mock(), ExplorerScope(), ExplorerFilters(minimum_node_document_count=2)
            )

        self.assertEqual(load.call_count, 2)
        self.assertEqual(smaller["stages"]["shown"]["nodes"], 2)
        self.assertEqual(smaller["filters"]["ranking_metric"], "degree")
        self.assertEqual(
            smaller["stages"]["edge_weight"], first["stages"]["edge_weight"]
        )
        self.assertNotEqual(
            stricter["stages"]["document_recurrence"],
            first["stages"]["document_recurrence"],
        )

    def test_changed_data_invalidates_the_cached_network(self) -> None:
        documents = [self._document(DOC_A, 2022)]
        with (
            patch("src.services.explorer._scoped_documents", return_value=documents),
            patch(
                "src.services.explorer.load_db_mentions", return_value=CORPUS
            ) as load,
        ):
            ExplorerService.network(Mock(), ExplorerScope(), ExplorerFilters())
            ExplorerService.network(Mock(), ExplorerScope(), ExplorerFilters())
            self.fingerprint.return_value = (8, 5, "t2")
            ExplorerService.network(Mock(), ExplorerScope(), ExplorerFilters())

        self.assertEqual(load.call_count, 2)

    def test_scopes_with_different_documents_do_not_share_networks(self) -> None:
        with (
            patch(
                "src.services.explorer._scoped_documents",
                side_effect=[
                    [self._document(DOC_A, 2022)],
                    [self._document(DOC_B, 2025)],
                ],
            ),
            patch(
                "src.services.explorer.load_db_mentions", return_value=CORPUS
            ) as load,
        ):
            ExplorerService.network(Mock(), ExplorerScope(), ExplorerFilters())
            ExplorerService.network(Mock(), ExplorerScope(), ExplorerFilters())

        self.assertEqual(load.call_count, 2)

    def test_unknown_ranking_metric_fails_before_querying(self) -> None:
        db = Mock()

        with self.assertRaises(ExplorerFiltroInvalido):
            ExplorerService.network(
                db, ExplorerScope(), ExplorerFilters(ranking_metric="eigenvector")
            )
        db.execute.assert_not_called()

    def test_compare_computes_each_period_without_top_n(self) -> None:
        calls = []

        def fake_network(db, scope, filters):
            calls.append((scope.period, filters.top_n))
            return [], build_explorer_network(
                CORPUS, ExplorerFilters(minimum_node_document_count=1, top_n=None)
            )

        with patch.object(
            ExplorerService, "_network_for_scope", side_effect=fake_network
        ):
            payload = ExplorerService.compare(
                Mock(),
                ExplorerScope(),
                ExplorerFilters(top_n=10),
                periods=["2024-2026", "2021-2023"],
                top_k=3,
            )

        self.assertEqual(calls, [("2021-2023", None), ("2024-2026", None)])
        # La respuesta debe cumplir el contrato público completo.
        ExplorerCompareResponse.model_validate(payload)
        self.assertEqual(payload["periods"], ["2021-2023", "2024-2026"])
        self.assertEqual(len(payload["period_summaries"]), 2)


class ExplorerApiTests(unittest.TestCase):
    def test_openapi_exposes_explorer_endpoints(self) -> None:
        paths = app.openapi()["paths"]

        self.assertIn("get", paths["/analysis/explorer/v1/meta"])
        self.assertIn("post", paths["/analysis/explorer/v1/network"])
        self.assertIn("post", paths["/analysis/explorer/v1/compare"])
        self.assertIn("get", paths["/analysis/explorer/v1/evidence"])

    def test_request_schema_rejects_unknown_categories_and_bad_pairs(self) -> None:
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(categories=["GOVERNANZA"])
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(link_mode="pairs", category_pairs=[["CHAR"]])
        with self.assertRaises(ValidationError):
            ExplorerCompareRequest(periods=["2021-2023"])

    def test_network_endpoint_maps_filter_errors_to_422(self) -> None:
        body = ExplorerNetworkRequest(categories=["CHAR"], link_mode="between")
        with (
            patch("src.services.explorer._scoped_documents", return_value=[]),
            self.assertRaises(ExplorerFiltroInvalido) as raised,
        ):
            explorer_network(body=body, db=Mock())

        self.assertEqual(raised.exception.codigo_http, 422)
        self.assertIn("between", raised.exception.mensaje)

    def test_data_fingerprint_summarizes_mentions_of_scoped_documents(self) -> None:
        db = Mock()
        db.execute.return_value.one.return_value = (120, 40, "2026-10-27")

        self.assertEqual(_data_fingerprint(db, []), ())
        db.execute.assert_not_called()

        documents = [SimpleNamespace(id=UUID(DOC_A)), SimpleNamespace(id=UUID(DOC_B))]
        self.assertEqual(_data_fingerprint(db, documents), (120, 40, "2026-10-27"))
        where = str(db.execute.call_args.args[0].whereclause)
        self.assertIn("entities.document_id IN", where)

    def test_excluded_entity_ids_are_validated_sorted_and_deduplicated(self) -> None:
        first = "00000000-0000-0000-0000-0000000000f1"
        second = "00000000-0000-0000-0000-0000000000f2"
        request = ExplorerNetworkRequest(excluded_entity_ids=[second, first, second])

        self.assertEqual(_filters(request, 10).excluded_entity_ids, (first, second))
        self.assertEqual(_filters(ExplorerNetworkRequest(), 10).excluded_entity_ids, ())
        with self.assertRaises(ValidationError):
            ExplorerNetworkRequest(excluded_entity_ids=["MADRE DE DIOS"])

    def test_excluded_entity_names_defaults_normalization_and_override(self) -> None:
        default_names = DEFAULT_EXCLUDED_ENTITY_NAMES
        self.assertEqual(
            _filters(ExplorerNetworkRequest(), 10).excluded_entity_names, default_names
        )
        self.assertEqual(
            _filters(ExplorerCompareRequest(), None).excluded_entity_names, default_names
        )
        request = ExplorerNetworkRequest(
            excluded_entity_names=[" Madre  de Dios ", "AGROFORESTRY", "agroforestry"]
        )
        self.assertEqual(
            _filters(request, 10).excluded_entity_names, ("agroforestry", "madre de dios")
        )
        self.assertEqual(
            _filters(ExplorerNetworkRequest(excluded_entity_names=[]), 10).excluded_entity_names,
            (),
        )
        self.assertEqual(
            _filters(ExplorerNetworkRequest(excluded_entity_names=["Podas"]), 10).excluded_entity_names,
            ("podas",),
        )
        for invalid in (["  "], [""], ["..."], ["---"], ["x" * 201], ["x"] * 501, None):
            with self.subTest(invalid=repr(invalid)[:30]):
                with self.assertRaises(ValidationError):
                    ExplorerNetworkRequest(excluded_entity_names=invalid)

    def test_scoped_name_exclusions_api_defaults_override_and_validation(self):
        for request in (ExplorerNetworkRequest(), ExplorerCompareRequest()):
            self.assertEqual(
                _filters(request, None).excluded_entity_names_by_category,
                DEFAULT_EXCLUDED_ENTITY_NAMES_BY_CATEGORY,
            )
        request = ExplorerNetworkRequest(excluded_entity_names_by_category={
            "LOC": [" P.E.M. ", "Área", "ÁREA"], "KNOW": ["Knowledge"], "ATT": ["Attitude"],
        })
        filters = _filters(request, 10)
        self.assertEqual(filters.excluded_entity_names_by_category, (
            ("KAS", ("attitude", "knowledge")), ("LOC", ("area", "pem")),
        ))
        self.assertEqual(_filters(ExplorerNetworkRequest(
            excluded_entity_names_by_category={}
        ), 10).excluded_entity_names_by_category, ())
        for value in ({"INVALID": ["place"]}, {"LOC": ["---"]}, {"LOC": ["x" * 201]},
                      {"LOC": ["x"] * 501}, None):
            with self.subTest(value=str(value)[:30]):
                with self.assertRaises(ValidationError):
                    ExplorerNetworkRequest(excluded_entity_names_by_category=value)

    def test_load_db_mentions_with_empty_document_list_returns_nothing(self) -> None:
        db = Mock()

        self.assertEqual(load_db_mentions(document_ids=[], db=db), [])
        db.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
