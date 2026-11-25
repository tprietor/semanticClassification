import os
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from src.models.canonical_entities import CanonicalEntity
from src.controlled_vocabulary import (
    BRAZIL_NUT_RULE_ID,
    ROAD_EXCLUDED_ENTITY_NAMES, ROAD_RULE_ID, is_road_pavement_alias,
)
from src.services.fuzzy_matching import (
    FuzzyMatchingDataError,
    RESOLUTION_VERSION,
    asociar_entidades_canonicas,
    canonicalizar_actor_generico,
    normalizar_nombre,
)


def canonical(name: str, category: str) -> CanonicalEntity:
    return CanonicalEntity(id=uuid4(), canonical_name=name, category=category)


def mention(text: str, category: str) -> dict:
    return {
        "text": text,
        "category": category,
        "start": 0,
        "end": len(text),
        "sentence_id": "s-000000000",
        "context": text,
        "ambiguity": "low",
    }


class FuzzyMatchingLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Mock()
        aliases_read_patcher = patch(
            "src.services.fuzzy_matching.CanonicalEntityAliasRepo.leer_todos",
            return_value=[],
        )
        aliases_register_patcher = patch(
            "src.services.fuzzy_matching.CanonicalEntityAliasRepo.registrar"
        )
        self.aliases_read = aliases_read_patcher.start()
        self.aliases_register = aliases_register_patcher.start()
        self.addCleanup(aliases_register_patcher.stop)
        self.addCleanup(aliases_read_patcher.stop)

    def test_normalization_ignores_case_accents_and_repeated_spaces(self) -> None:
        self.assertEqual(
            normalizar_nombre("  RÍO   Madre de Dios "),
            "rio madre de dios",
        )

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_protected_areas_consolidates_loc_aliases_and_keeps_other_nodes(self, read, create):
        target = canonical("protected areas", "LOC")
        excluded = canonical("non-ACP private lands", "LOC")
        regulation = canonical("1997 Law of Protected Areas", "RUL")
        unrelated_acronym = canonical("PAs", "CHAR")
        read.return_value = [target, excluded, regulation, unrelated_acronym, canonical("ACPs", "LOC")]
        aliases = ["protected area", "PPAs", "PAs", "ACPs", "ACP", "privately conserved areas",
                   "private lands", "Private conservation area (ACP)", "Privately protected areas"]
        sources = [mention(alias, "LOC") for alias in aliases] + [
            mention(item.canonical_name, item.category) for item in (excluded, regulation, unrelated_acronym)
        ]
        result, _ = asociar_entidades_canonicas(self.db, sources)
        self.assertEqual([item["canonical_id"] for item in result],
                         [target.id] * len(aliases) + [excluded.id, regulation.id, unrelated_acronym.id])
        self.assertEqual([item["text"] for item in result], [item["text"] for item in sources])
        create.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_unprotected_areas_cannot_use_protected_areas_as_fuzzy_candidate(self, read, create):
        read.return_value = [canonical("protected areas", "LOC")]
        create.return_value = canonical("unprotected areas", "LOC")
        result, _ = asociar_entidades_canonicas(self.db, [mention("unprotected areas", "LOC")])
        self.assertEqual(result[0]["canonical_name"], "unprotected areas")
        create.assert_called_once_with(self.db, canonical_name="unprotected areas", category="LOC")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_monoculture_singularizes_only_standalone_practice_names(self, read, create):
        singular = canonical("monoculture", "PRAC")
        plural = canonical("monocultures", "PRAC")
        compounds = [canonical(label, "PRAC") for label in (
            "cacao monoculture", "Coffee Monoculture System", "abandonment of monocultures",
        )]
        read.return_value = [singular, plural, *compounds]
        sources = [mention(label, "PRAC") for label in (
            "monoculture", "Monocultures", "monocultures",
            *(compound.canonical_name for compound in compounds),
        )]
        result, _ = asociar_entidades_canonicas(self.db, sources)
        self.assertEqual([item["canonical_id"] for item in result],
                         [singular.id] * 3 + [compound.id for compound in compounds])
        self.assertEqual([item["text"] for item in result], [item["text"] for item in sources])
        create.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_homegardens_resolves_to_existing_homegarden_in_prac(self, read):
        target = canonical("homegarden", "PRAC")
        spaced = canonical("home gardens", "PRAC")
        loc = canonical("homegardens", "LOC")
        read.return_value = [target, spaced, loc, canonical("homegardens", "PRAC")]
        sources = [mention("Homegardens", "PRAC"), mention("HOMEGARDENS", "PRAC"),
                   mention("homegarden", "PRAC"), mention("home gardens", "PRAC"),
                   mention("homegardens", "LOC")]
        result, _ = asociar_entidades_canonicas(self.db, sources)
        self.assertEqual([item["canonical_id"] for item in result], [target.id] * 3 + [spaced.id, loc.id])
        self.assertEqual([item["text"] for item in result], [item["text"] for item in sources])

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_community_aliases_resolve_to_three_distinct_nodes(self, read, create):
        groups = {
            "Indigenous Peoples": ["ip", "IP", "IPs", "Indigenous communities", "pueblos indígenas"],
            "local communities": ["LC", "lc", "LCs", "Local Communities", "local communitie", "comunidades locales"],
            "IPLCs": ["ipLcs", "IPLC", "Indigenous peoples and local communities",
                      "comunidades locales e indígenas"],
            "Social Progress Index": ["IPS"],
        }
        targets = {name: canonical(name, "CHAR") for name in groups}
        read.return_value = [canonical("LC", "CHAR"), *targets.values()]
        sources = [
            mention(form, "CHAR") if name != "Social Progress Index"
            else dict(mention(form, "CHAR"), context="according to the Social Progress Index (IPS 2021)")
            for name, forms in groups.items() for form in forms
        ]
        result, _ = asociar_entidades_canonicas(self.db, sources)
        expected = [targets[name].id for name, forms in groups.items() for _ in forms]
        self.assertEqual([item["canonical_id"] for item in result], expected)
        self.assertEqual([item["text"] for item in result], [item["text"] for item in sources])
        create.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_joint_source_span_remains_distinct_from_sentence_cooccurrence(self, read):
        read.return_value = [canonical(name, "CHAR") for name in ("local communities", "IPLCs", "Indigenous Peoples")]
        joint = "Indigenous Peoples (IPs) and Local Communities (LCs) defend territories."
        separate = "IPs maintain forests; LCs monitor rivers."
        sources = []
        for start, context, texts in ((10, joint, ("Indigenous Peoples", "IPs", "Local Communities", "LCs")),
                                      (200, separate, ("IPs", "LCs"))):
            for form in texts:
                offset = start + context.index(form)
                sources.append(dict(mention(form, "CHAR"), start=offset, end=offset + len(form),
                                    sentence_id=f"s-{start:09}", context=context))
        result, _ = asociar_entidades_canonicas(self.db, sources)
        self.assertEqual([item["canonical_name"] for item in result],
                         ["IPLCs", "Indigenous Peoples", "local communities"])
        self.assertEqual(result[0]["text"], "Indigenous Peoples (IPs) and Local Communities (LCs)")
        self.assertEqual(result[0]["resolution_details"]["source_mentions"], sources[:4])

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_brazil_nut_repairs_exact_occurrence_and_preserves_country_and_source(self, read, create):
        country, resource = canonical("Brazil", "LOC"), canonical("Brazil nut", "eco_INFRA")
        read.return_value = [country, resource]
        text = "Brazil exports Brazil nuts."
        source = [dict(mention("Brazil", "LOC"), start=100, end=106,
                       sentence_id="s-000000100", context=text),
                  dict(mention("Brazil", "LOC"), start=115, end=121,
                       sentence_id="s-000000100", context=text)]
        before = copy.deepcopy(source)
        result, _ = asociar_entidades_canonicas(self.db, source)
        self.assertEqual(source, before)
        self.assertEqual((result[0]["canonical_id"], result[0]["category"]), (country.id, "LOC"))
        nut = result[1]
        self.assertEqual((nut["text"], nut["start"], nut["end"]), ("Brazil nuts", 115, 126))
        self.assertEqual((nut["canonical_id"], nut["category"]), (resource.id, "eco_INFRA"))
        self.assertEqual(nut["resolution_details"]["source_mention"], before[1])
        self.assertEqual(nut["resolution_details"]["rule"], BRAZIL_NUT_RULE_ID)
        # A country alias must never be added to the resource's dictionary.
        resource_aliases = [call.kwargs["alias_text"] for call in self.aliases_register.call_args_list
                            if call.kwargs["canonical_id"] == resource.id]
        self.assertEqual(resource_aliases, ["Brazil nuts"])
        create.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_complete_nut_variants_force_eco_without_fuzzy_reusing_longer_names(self, read, create):
        read.return_value = [canonical("Brazil nuts", "PRAC"), canonical("Brazil nut forests", "eco_INFRA")]
        resource = canonical("Brazil nut", "eco_INFRA")
        create.return_value = resource
        result, stats = asociar_entidades_canonicas(self.db, [
            mention("Brazil nut", "LOC"), mention("Brazil Nuts", "PRAC"), mention("Brazil-nut", "CHAR"),
        ])
        self.assertEqual({r["canonical_id"] for r in result}, {resource.id})
        self.assertEqual({r["category"] for r in result}, {"eco_INFRA"})
        self.assertEqual(stats["controlled_alias"], 3)
        create.assert_called_once_with(self.db, canonical_name="Brazil nut", category="eco_INFRA")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_brazil_nut_repair_rejects_overlapping_annotations(self, read):
        source = [dict(mention("Brazil", "LOC"), context="Brazil nuts"),
                  dict(mention("nuts", "eco_INFRA"), start=7, end=11, context="Brazil nuts")]
        with self.assertRaisesRegex(FuzzyMatchingDataError, "superpuesta"):
            asociar_entidades_canonicas(self.db, source)
        read.assert_not_called()

    def test_brazil_nut_requires_anchored_source_and_leaves_compounds_unchanged(self):
        from src.services.fuzzy_matching import _completar_brazil_nut, _planear_menciones
        source = [dict(mention("Brazil", "LOC"), context="Brazil and Brazil nuts"),
                  dict(mention("Brazil", "LOC"), context="Brazil nuts", start=5, end=11),
                  dict(mention("Brazil", "LOC"), context="Brazil nuts", sentence_id="unknown"),
                  mention("Brazil nut harvesting", "PRAC"),
                  mention("Brazil nut gatherers", "CHAR")]
        self.assertEqual(_completar_brazil_nut(source), source)
        self.assertTrue(all(p.strategy == "standard" for p in _planear_menciones(source)))

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_road_variants_share_physical_canonical_and_preserve_evidence(self, read, create):
        target = canonical("road pavement", "physical_INFRA")
        read.return_value = [target, canonical("road pavement", "PRAC")]
        original = [mention("road corridor", "LOC"), mention("road building", "PRAC"),
                    mention("Road networks", "physical_INFRA"), mention("road pavement", "PRAC"),
                    mention("Road", "CHAR"), mention("Road Surface", "CHAR")]
        result, stats = asociar_entidades_canonicas(self.db, original)
        self.assertEqual({r["canonical_id"] for r in result}, {target.id})
        self.assertEqual({r["category"] for r in result}, {"physical_INFRA"})
        self.assertEqual(stats["controlled_alias"], 6)
        for before, after in zip(original, result, strict=True):
            for key in ("text", "start", "end", "sentence_id", "context", "ambiguity"):
                self.assertEqual(before[key], after[key])
            self.assertEqual(after["resolution_details"]["source_category"], before["category"])
            self.assertEqual(after["resolution_details"]["rule"], ROAD_RULE_ID)
        self.assertEqual([m["category"] for m in original], ["LOC", "PRAC", "physical_INFRA", "PRAC", "CHAR", "CHAR"])
        create.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_road_rule_creates_physical_canonical_instead_of_reusing_practice(self, read, create):
        read.return_value = [canonical("road pavement", "PRAC"), canonical("road pavement maintenance", "physical_INFRA")]
        target = canonical("road pavement", "physical_INFRA")
        create.return_value = target
        result, _ = asociar_entidades_canonicas(self.db, [mention("road pavement", "PRAC")])
        create.assert_called_once_with(self.db, canonical_name="road pavement", category="physical_INFRA")
        self.assertEqual(result[0]["canonical_id"], target.id)

    def test_road_rule_respects_exclusions_and_word_boundaries(self):
        for text in (*ROAD_EXCLUDED_ENTITY_NAMES, "NEW ROADS.", "new-road", "railroads", "roadmap", "broader social circles", "broadcast sowing"):
            with self.subTest(text=text):
                self.assertFalse(is_road_pavement_alias(text))
        for text in ("road", "ROAD PAVEMENT", "road networks", "rural roads", "road’s surface"):
            with self.subTest(text=text):
                self.assertTrue(is_road_pavement_alias(text))

    def test_wyss_institution_forms_must_be_char(self) -> None:
        for text in ("Wyss Academy", "WA SAM Hub", "WA Sam Hub"):
            with self.subTest(text=text), self.assertRaisesRegex(
                FuzzyMatchingDataError, "debe ser CHAR"
            ):
                asociar_entidades_canonicas(self.db, [mention(text, "LOC")])

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_wa_sam_hub_char_is_accepted(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("WA SAM Hub", "CHAR")
        leer_todas.return_value = [existing]

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("WA Sam Hub", "CHAR")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        crear.assert_not_called()

    def test_agroforestry_systems_cannot_be_loc(self) -> None:
        with self.assertRaisesRegex(FuzzyMatchingDataError, "debe ser PRAC"):
            asociar_entidades_canonicas(
                self.db, [mention("Agroforestry Systems", "LOC")]
            )

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_agroforestry_systems_prac_is_accepted(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Agroforestry Systems", "PRAC")
        leer_todas.return_value = [existing]

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("agroforestry systems", "PRAC")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_exact_normalized_match_reuses_canonical(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Madre de Dios", "LOC")
        leer_todas.return_value = [existing]

        result, stats = asociar_entidades_canonicas(
            self.db, [mention("MADRE DE DIÓS", "LOC")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        self.assertEqual(result[0]["match_type"], "exact")
        self.assertEqual(stats["exact"], 1)
        self.assertEqual(sum(stats.values()), 1)
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_candidates_from_other_categories_are_not_reused(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = [canonical("Madre de Dios", "CHAR")]
        new = canonical("Madre de Dios", "LOC")
        crear.return_value = new

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("Madre de Dios", "LOC")]
        )

        self.assertEqual(result[0]["canonical_id"], new.id)
        self.assertEqual(result[0]["match_type"], "new")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_strong_fuzzy_match_reuses_clear_candidate(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Puerto Maldonado", "LOC")
        leer_todas.return_value = [existing]

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("Puerto Maldonadoo", "LOC")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        self.assertEqual(result[0]["match_type"], "fuzzy")
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching._puntaje", side_effect=[97.0, 95.0])
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_close_second_candidate_prevents_automatic_merge(
        self, leer_todas: Mock, crear: Mock, _puntaje: Mock
    ) -> None:
        leer_todas.return_value = [
            canonical("Ley Marco del Ambiente", "RUL"),
            canonical("Ley Marco Ambiental", "RUL"),
        ]
        new = canonical("Ley Marco Ambiente", "RUL")
        crear.return_value = new

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("Ley Marco Ambiente", "RUL")]
        )

        self.assertEqual(result[0]["canonical_id"], new.id)
        self.assertEqual(result[0]["match_type"], "new")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_short_terms_require_exact_match(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = [canonical("Oro", "PRAC")]
        new = canonical("Ora", "PRAC")
        crear.return_value = new

        result, _ = asociar_entidades_canonicas(self.db, [mention("Ora", "PRAC")])

        self.assertEqual(result[0]["canonical_id"], new.id)
        self.assertEqual(result[0]["match_type"], "new")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_saf_prac_forms_share_agroforestry_canonical(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Sistemas Agroflorestais", "PRAC")
        leer_todas.return_value = [existing]
        forms = [
            "SAF", "SAFs", "SAF-A", "SAF-F", "SAFs-A", "SAFs-F",
            "SAF-A/F", "SAFs-A/F", "Sistemas Agroflorestais",
        ]

        result, stats = asociar_entidades_canonicas(
            self.db, [mention(form, "PRAC") for form in forms]
        )

        self.assertEqual([item["text"] for item in result], forms)
        self.assertEqual({item["canonical_id"] for item in result}, {existing.id})
        self.assertEqual(stats["controlled_alias"], len(forms) - 1)
        self.assertEqual(result[-1]["match_type"], "exact")
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_saf_rule_does_not_merge_other_categories(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = [canonical("Sistemas Agroflorestais", "PRAC")]
        other = canonical("SAF", "CHAR")
        crear.return_value = other

        result, stats = asociar_entidades_canonicas(self.db, [mention("SAF", "CHAR")])

        self.assertEqual(result[0]["canonical_id"], other.id)
        self.assertEqual(stats["controlled_alias"], 0)
        crear.assert_called_once_with(self.db, canonical_name="SAF", category="CHAR")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas", return_value=[])
    def test_saf_alias_creates_one_full_name_canonical_when_absent(
        self, _leer_todas: Mock, crear: Mock
    ) -> None:
        created = canonical("Sistemas Agroflorestais", "PRAC")
        crear.return_value = created

        result, stats = asociar_entidades_canonicas(
            self.db, [mention("SAFs-F", "PRAC"), mention("SAF", "PRAC")]
        )

        self.assertEqual({item["canonical_id"] for item in result}, {created.id})
        self.assertEqual(stats["controlled_alias"], 2)
        crear.assert_called_once_with(
            self.db, canonical_name="Sistemas Agroflorestais", category="PRAC"
        )

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_legacy_gov_mentions_are_normalized_to_rul(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = []
        created = canonical("Ley Forestal", "RUL")
        crear.return_value = created
        legacy_mention = mention("Ley Forestal", "GOV")

        result, _ = asociar_entidades_canonicas(self.db, [legacy_mention])

        self.assertEqual(legacy_mention["category"], "RUL")
        self.assertEqual(result[0]["category"], "RUL")
        self.assertEqual(result[0]["canonical_id"], created.id)
        crear.assert_called_once_with(
            self.db, canonical_name="Ley Forestal", category="RUL"
        )

    def test_controlled_singularization_preserves_gender_and_phrase(self) -> None:
        self.assertEqual(canonicalizar_actor_generico("MINEROS"), "minero")
        self.assertEqual(canonicalizar_actor_generico("mineras"), "minera")
        self.assertEqual(canonicalizar_actor_generico("docentes"), "docente")
        self.assertEqual(canonicalizar_actor_generico("presidentes"), "presidente")
        self.assertEqual(
            canonicalizar_actor_generico("mineros artesanales"),
            "minero artesanal",
        )
        self.assertIsNone(
            canonicalizar_actor_generico("Asociación de Pequeños Mineros")
        )
        self.assertIsNone(
            canonicalizar_actor_generico("mineros que abandonaron la minería")
        )
        self.assertIsNone(canonicalizar_actor_generico("varones o mujeres"))

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_generic_actor_variants_converge_without_losing_original_text(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = []
        created: list[CanonicalEntity] = []

        def create_canonical(_: Mock, canonical_name: str, category: str):
            item = canonical(canonical_name, category)
            created.append(item)
            return item

        crear.side_effect = create_canonical
        inputs = [
            mention("MINEROS", "CHAR"),
            mention("mineros", "CHAR"),
            mention("minero", "CHAR"),
            mention("mineras", "CHAR"),
            mention("minera", "CHAR"),
        ]

        result, stats = asociar_entidades_canonicas(self.db, inputs)

        self.assertEqual(
            [item.canonical_name for item in created], ["minero", "minera"]
        )
        self.assertEqual({item["canonical_id"] for item in result[:3]}, {created[0].id})
        self.assertEqual({item["canonical_id"] for item in result[3:]}, {created[1].id})
        self.assertNotEqual(created[0].id, created[1].id)
        self.assertEqual(
            [item["text"] for item in result], [item["text"] for item in inputs]
        )
        self.assertEqual(stats["morphology"], 3)
        self.assertTrue(
            all(item["resolution_version"] == RESOLUTION_VERSION for item in result)
        )

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_generic_actor_qualifier_remains_a_distinct_identity(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = []
        created: list[CanonicalEntity] = []

        def create_canonical(_: Mock, canonical_name: str, category: str):
            item = canonical(canonical_name, category)
            created.append(item)
            return item

        crear.side_effect = create_canonical

        result, _ = asociar_entidades_canonicas(
            self.db,
            [mention("mineros", "CHAR"), mention("mineros artesanales", "CHAR")],
        )

        self.assertEqual(
            [item.canonical_name for item in created],
            ["minero", "minero artesanal"],
        )
        self.assertNotEqual(result[0]["canonical_id"], result[1]["canonical_id"])

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_document_person_variants_resolve_to_longest_full_name(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Griselda Zubizarreta Vargas", "CHAR")
        leer_todas.return_value = [existing]

        result, stats = asociar_entidades_canonicas(
            self.db,
            [
                mention("Griselda Zubizarreta Vargas", "CHAR"),
                mention("Griselda Zubizarreta", "CHAR"),
                mention("Griselda", "CHAR"),
            ],
        )

        self.assertEqual({item["canonical_id"] for item in result}, {existing.id})
        self.assertEqual(result[0]["match_type"], "exact")
        self.assertEqual(result[1]["match_type"], "person_alias")
        self.assertEqual(result[2]["match_type"], "person_alias")
        self.assertEqual(stats["person_alias"], 2)
        self.assertEqual(
            result[2]["resolution_details"]["rule"],
            "unique_document_name_prefix",
        )
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_bare_first_name_is_not_merged_when_document_has_two_families(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = []

        def create_canonical(_: Mock, canonical_name: str, category: str):
            return canonical(canonical_name, category)

        crear.side_effect = create_canonical
        result, _ = asociar_entidades_canonicas(
            self.db,
            [
                mention("Griselda Pérez", "CHAR"),
                mention("Griselda Zubizarreta", "CHAR"),
                mention("Griselda", "CHAR"),
            ],
        )

        self.assertEqual(len({item["canonical_id"] for item in result}), 3)
        self.assertEqual(result[2]["match_type"], "new")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_corporate_suffix_is_not_treated_as_a_person_surname(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        leer_todas.return_value = []

        def create_canonical(_: Mock, canonical_name: str, category: str):
            return canonical(canonical_name, category)

        crear.side_effect = create_canonical
        result, _ = asociar_entidades_canonicas(
            self.db,
            [mention("Conirsa", "CHAR"), mention("Conirsa SA", "CHAR")],
        )

        self.assertEqual(len({item["canonical_id"] for item in result}), 2)
        self.assertNotIn("person_alias", {item["match_type"] for item in result})

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_academy_prefix_is_not_treated_as_a_person_name(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        academy = canonical("Wyss Academy for Nature", "CHAR")
        hub = canonical("Wyss Academy Hub South America", "CHAR")
        new = canonical("Wyss Academy", "CHAR")
        leer_todas.return_value = [academy, hub]
        crear.return_value = new

        result, _ = asociar_entidades_canonicas(
            self.db,
            [
                mention("Wyss Academy", "CHAR"),
                mention("Wyss Academy Hub South America", "CHAR"),
            ],
        )

        self.assertNotEqual(result[0]["canonical_id"], hub.id)
        self.assertNotEqual(result[0]["match_type"], "person_alias")
        crear.assert_called_once()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_unique_longer_person_name_can_resolve_two_token_variant(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Griselda Zubizarreta Vargas", "CHAR")
        leer_todas.return_value = [existing]

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("Griselda Zubizarreta", "CHAR")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        self.assertEqual(result[0]["match_type"], "person_name")
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_unique_stored_multiword_alias_is_reused(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Griselda Zubizarreta Vargas", "CHAR")
        leer_todas.return_value = [existing]
        self.aliases_read.return_value = [
            SimpleNamespace(
                canonical_id=existing.id,
                normalized_alias=normalizar_nombre("G. Zubizarreta"),
            )
        ]

        result, _ = asociar_entidades_canonicas(
            self.db, [mention("G. Zubizarreta", "CHAR")]
        )

        self.assertEqual(result[0]["canonical_id"], existing.id)
        self.assertEqual(result[0]["match_type"], "stored_alias")
        crear.assert_not_called()

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_stored_bare_first_name_is_not_reused_without_document_anchor(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Griselda Zubizarreta Vargas", "CHAR")
        new = canonical("Griselda", "CHAR")
        leer_todas.return_value = [existing]
        crear.return_value = new
        self.aliases_read.return_value = [
            SimpleNamespace(
                canonical_id=existing.id,
                normalized_alias=normalizar_nombre("Griselda"),
            )
        ]

        result, _ = asociar_entidades_canonicas(self.db, [mention("Griselda", "CHAR")])

        self.assertEqual(result[0]["canonical_id"], new.id)
        self.assertEqual(result[0]["match_type"], "new")

    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.crear")
    @patch("src.services.fuzzy_matching.CanonicalEntityRepo.leer_todas")
    def test_stored_single_word_institution_alias_is_reused(
        self, leer_todas: Mock, crear: Mock
    ) -> None:
        existing = canonical("Wyss Academy for Nature", "CHAR")
        leer_todas.return_value = [existing]
        self.aliases_read.return_value = [
            SimpleNamespace(
                canonical_id=existing.id,
                normalized_alias=normalizar_nombre("Wyss"),
            )
        ]

        result, _ = asociar_entidades_canonicas(self.db, [mention("WYSS", "CHAR")])

        self.assertEqual(result[0]["canonical_id"], existing.id)
        self.assertEqual(result[0]["match_type"], "stored_alias")
        crear.assert_not_called()


if __name__ == "__main__":
    unittest.main()
