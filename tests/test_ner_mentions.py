import os
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

if "anthropic" not in sys.modules:
    anthropic_stub = types.ModuleType("anthropic")
    anthropic_stub.Anthropic = type("Anthropic", (), {})
    sys.modules["anthropic"] = anthropic_stub

from src.services.ner import _parsear_datos, _segmentar_oraciones
from src.services import ner


class NerProviderValidationTests(unittest.TestCase):
    def test_brazil_nut_retry_restores_complete_resource_and_keeps_country(self):
        client = Mock()
        def respond(**request):
            corrected = client.messages.create.call_count > 1
            annotations = [
                {"label": "LOC", "text": "Brazil", "sentence_id": "s-000000000", "ambiguity": "low"},
                {"label": "eco_INFRA" if corrected else "LOC",
                 "text": "Brazil nuts" if corrected else "Brazil",
                 "sentence_id": "s-000000000", "ambiguity": "low"},
            ]
            return SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
                type="tool_use", name=ner.NER_TOOL_NAME,
                input={"document_id": "doc", "annotations": annotations})])
        client.messages.create.side_effect = respond
        with patch.object(ner, "get_anthropic_client", return_value=client):
            entities = ner.extraer_entidades("Brazil exports Brazil nuts.", "doc")
        self.assertEqual(client.messages.create.call_count, 2)
        self.assertEqual([(e["text"], e["category"], e["start"], e["end"]) for e in entities],
                         [("Brazil", "LOC", 0, 6), ("Brazil nuts", "eco_INFRA", 15, 26)])

    def test_conflicting_spans_are_corrected_before_accepting_chunk(self):
        client = Mock()
        calls = []

        def respond(**request):
            calls.append(request)
            annotations = [{"label": "PRAC", "text": "capacitación", "sentence_id": "s-000000000", "ambiguity": "low"},
                           {"label": "CHAR", "text": "productoras", "sentence_id": "s-000000000", "ambiguity": "low"}]
            if len(calls) == 1:
                annotations[0]["text"] = "capacitación a las productoras"
            return SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
                type="tool_use", name=ner.NER_TOOL_NAME,
                input={"document_id": "real-document", "annotations": annotations})])

        client.messages.create.side_effect = respond
        with patch.object(ner, "get_anthropic_client", return_value=client):
            entities = ner.extraer_entidades("capacitación a las productoras.", "real-document")
        self.assertEqual(len(calls), 2)
        self.assertIn("validation_issues", calls[1]["messages"][1]["content"])
        self.assertEqual([e["text"] for e in entities], ["capacitación", "productoras"])

    def test_persistent_invalid_response_fails_instead_of_returning_partial_result(self):
        client = Mock()
        client.messages.create.return_value = SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
            type="tool_use", name=ner.NER_TOOL_NAME,
            input={"document_id": "document", "annotations": [{"label": "CHAR", "text": "inventado",
                   "sentence_id": "s-000000000", "ambiguity": "low"}]})])
        with patch.object(ner, "get_anthropic_client", return_value=client):
            with self.assertRaisesRegex(RuntimeError, "inválida tras 2 correcciones"):
                ner.extraer_entidades("Las productoras participan.", "document")
        self.assertEqual(client.messages.create.call_count, 3)

    def test_wrong_document_id_is_rejected_even_for_empty_annotations(self):
        client = Mock()
        client.messages.create.return_value = SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
            type="tool_use", name=ner.NER_TOOL_NAME,
            input={"document_id": "other-document", "annotations": []})])
        with patch.object(ner, "get_anthropic_client", return_value=client):
            with self.assertRaisesRegex(RuntimeError, "document_id"):
                ner.extraer_entidades("Gracias por su atención.", "document")


class NerMentionPositionTests(unittest.TestCase):
    def test_complete_brazil_nut_with_wrong_category_is_rejected(self):
        issues = []
        sentences = _segmentar_oraciones("Brazil nut grows here.", 0)
        entities = _parsear_datos({"document_id": "doc", "annotations": [
            {"label": "LOC", "text": "Brazil nut", "sentence_id": sentences[0]["sentence_id"], "ambiguity": "low"},
        ]}, sentences, issues)
        self.assertEqual(entities, [])
        self.assertTrue(any("eco_INFRA" in issue for issue in issues))

    def test_et_al_citation_does_not_split_sentence(self) -> None:
        text = "Chamberlain et al. [23] studied agroforestry. Farmers participated."
        sentences = _segmentar_oraciones(text, 0)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0]["text"], "Chamberlain et al. [23] studied agroforestry.")

    def test_figure_and_reference_citations_do_not_split_sentence(self) -> None:
        text = "Rainfall changed (Fig. 1a), as reported in ref. 67. Forests recovered."
        sentences = _segmentar_oraciones(text, 0)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0]["text"], "Rainfall changed (Fig. 1a), as reported in ref. 67.")

    def test_section_citation_does_not_split_sentence(self) -> None:
        text = 'See Sect. "Results" for the agroforestry findings. Farmers participated.'
        sentences = _segmentar_oraciones(text, 0)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0]["text"], 'See Sect. "Results" for the agroforestry findings.')

    def test_annual_rate_and_figure_citation_remain_together(self) -> None:
        text = "Income rose 4% p.a. (Figure 5). Families adapted."
        sentences = _segmentar_oraciones(text, 0)
        self.assertEqual([s["text"] for s in sentences],
                         ["Income rose 4% p.a. (Figure 5).", "Families adapted."])

    def test_confer_figure_citation_remains_in_sentence(self) -> None:
        text = "Credit was scarce (conf. Figure 8). Farmers invested."
        sentences = _segmentar_oraciones(text, 0)
        self.assertEqual([s["text"] for s in sentences],
                         ["Credit was scarce (conf. Figure 8).", "Farmers invested."])

    def test_loc_inside_char_survives_in_either_response_order(self) -> None:
        text = "La comunidad de San Pedro decidió participar."
        sentences = _segmentar_oraciones(text, 83)
        annotations = [
            {"label": label, "text": span, "ambiguity": "low",
             "sentence_id": sentences[0]["sentence_id"]}
            for label, span in [("CHAR", "comunidad de San Pedro"), ("LOC", "San Pedro")]
        ]
        for ordered in (annotations, annotations[::-1]):
            with self.subTest(order=[a["label"] for a in ordered]):
                entities = _parsear_datos({"annotations": ordered}, sentences)
                self.assertEqual([e["category"] for e in entities], ["CHAR", "LOC"])
                for entity in entities:
                    self.assertEqual(entity["context"], text)
                    self.assertEqual(text[entity["start"] - 83:entity["end"] - 83], entity["text"])

    def test_repeated_nested_mentions_keep_each_position(self) -> None:
        text = "comunidad de San Pedro y comunidad de San Pedro."
        sentences = _segmentar_oraciones(text, 0)
        annotations = [
            {"label": label, "text": span, "ambiguity": "low",
             "sentence_id": sentences[0]["sentence_id"]}
            for label, span in [("CHAR", "comunidad de San Pedro"), ("LOC", "San Pedro")] * 2
        ]
        for ordered in (annotations, annotations[::-1]):
            with self.subTest(order=[a["label"] for a in ordered]):
                entities = _parsear_datos({"annotations": ordered}, sentences)
                self.assertEqual([(e["category"], e["start"]) for e in entities],
                                 [("CHAR", 0), ("LOC", 13), ("CHAR", 25), ("LOC", 38)])

    def test_nesting_does_not_enable_other_overlaps_or_same_span_labels(self) -> None:
        cases = [
            ("CHAR", "San Pedro", "LOC", "San Pedro"),
            ("LOC", "comunidad de San Pedro", "CHAR", "San Pedro"),
            ("PRAC", "restauración del bosque", "eco_INFRA", "bosque"),
            ("CHAR", "comunidad de San", "LOC", "San Pedro"),
        ]
        for first_label, first_span, second_label, second_span in cases:
            with self.subTest(case=(first_label, second_label, first_span)):
                text = "comunidad de San Pedro y restauración del bosque."
                sentences = _segmentar_oraciones(text, 0)
                annotations = [
                    {"label": label, "text": span, "ambiguity": "low",
                     "sentence_id": sentences[0]["sentence_id"]}
                    for label, span in [(first_label, first_span), (second_label, second_span)]
                ]
                with self.assertLogs("src.services.ner", level="WARNING"):
                    entities = _parsear_datos({"annotations": annotations}, sentences)
                self.assertEqual(len(entities), 1)

    def test_nonliteral_and_unknown_sentence_annotations_are_discarded(self) -> None:
        sentences = _segmentar_oraciones("Las productoras participan.", 0)
        annotations = [
            {"label": "CHAR", "text": "productora", "ambiguity": "low",
             "sentence_id": "unknown"},
            {"label": "CHAR", "text": "Productoras", "ambiguity": "low",
             "sentence_id": sentences[0]["sentence_id"]},
            {"label": "CHAR", "text": 42, "ambiguity": "low",
             "sentence_id": sentences[0]["sentence_id"]},
        ]
        with self.assertLogs("src.services.ner", level="WARNING"):
            self.assertEqual(_parsear_datos({"annotations": annotations}, sentences), [])

    def test_annotations_out_of_order_keep_document_positions(self) -> None:
        text = "La minería afectó el río.\n\n" "Las comunidades rechazaron la minería."
        sentences = _segmentar_oraciones(text, 0)
        first_id = sentences[0]["sentence_id"]
        second_id = sentences[1]["sentence_id"]
        response = {
            "annotations": [
                {
                    "sentence_id": second_id,
                    "label": "PRAC",
                    "text": "minería",
                    "ambiguity": "low",
                },
                {
                    "sentence_id": first_id,
                    "label": "LOC",
                    "text": "río",
                    "ambiguity": "low",
                },
                {
                    "sentence_id": first_id,
                    "label": "PRAC",
                    "text": "minería",
                    "ambiguity": "low",
                },
                {
                    "sentence_id": second_id,
                    "label": "CHAR",
                    "text": "comunidades",
                    "ambiguity": "low",
                },
            ]
        }

        entities = _parsear_datos(response, sentences)

        self.assertEqual(
            [entity["text"] for entity in entities],
            ["minería", "río", "comunidades", "minería"],
        )
        for entity in entities:
            self.assertEqual(text[entity["start"] : entity["end"]], entity["text"])

    def test_repeated_span_in_one_sentence_uses_each_occurrence(self) -> None:
        text = "minería y minería."
        sentences = _segmentar_oraciones(text, 0)
        sentence_id = sentences[0]["sentence_id"]
        annotation = {
            "sentence_id": sentence_id,
            "label": "PRAC",
            "text": "minería",
            "ambiguity": "low",
        }

        entities = _parsear_datos(
            {"annotations": [annotation, annotation.copy()]}, sentences
        )

        self.assertEqual(
            [(entity["start"], entity["end"]) for entity in entities],
            [(0, 7), (10, 17)],
        )

    def test_case_variants_are_distinct_mentions(self) -> None:
        text = "Minería y minería."
        sentences = _segmentar_oraciones(text, 0)
        sentence_id = sentences[0]["sentence_id"]
        response = {
            "annotations": [
                {
                    "sentence_id": sentence_id,
                    "label": "PRAC",
                    "text": "minería",
                    "ambiguity": "low",
                },
                {
                    "sentence_id": sentence_id,
                    "label": "PRAC",
                    "text": "Minería",
                    "ambiguity": "low",
                },
            ]
        }

        entities = _parsear_datos(response, sentences)

        self.assertEqual(
            [entity["text"] for entity in entities], ["Minería", "minería"]
        )
        self.assertEqual(
            [(entity["start"], entity["end"]) for entity in entities],
            [(0, 7), (10, 17)],
        )


if __name__ == "__main__":
    unittest.main()
