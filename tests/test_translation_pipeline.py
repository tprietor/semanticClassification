import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi import FastAPI

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
if "src.services.pdf_converter" not in sys.modules:
    pdf_converter_stub = types.ModuleType("src.services.pdf_converter")
    pdf_converter_stub.PdfConverter = type("PdfConverter", (), {})
    sys.modules["src.services.pdf_converter"] = pdf_converter_stub

from src.api.routers.documents import router
from src.config import settings
from src.services.documents import DocumentService, DocumentoError
from src.services.translation import (
    LanguageMismatchError,
    TranslationError,
    translate_to_english,
    verify_english_language,
)


class TranslationPipelineTests(unittest.TestCase):
    def test_english_document_is_copied_byte_for_byte_without_provider_or_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            document_id = uuid4()
            cleaned = Path(tmp) / "cleaned.txt"
            source = "Cacao — agroforestry.\n\nSecond paragraph.\n".encode("utf-8")
            cleaned.write_bytes(source)
            doc = SimpleNamespace(
                id=document_id,
                status="cleaned",
                language="en",
                cleaned_path=str(cleaned),
                english_path=None,
            )
            db = Mock()
            with (
                patch.object(settings, "STORAGE_ENGLISH", Path(tmp) / "english"),
                patch.object(settings, "ANTHROPIC_API_KEY", ""),
                patch("src.services.documents.DocumentRepo.leer_uno", return_value=doc),
                patch("src.services.documents.DocumentRepo.actualizar_status") as update,
                patch("src.services.documents.translate_to_english") as translate,
                patch(
                    "src.services.translation.get_anthropic_client",
                    side_effect=AssertionError("English passthrough must not contact Anthropic"),
                ) as client,
            ):
                result = DocumentService.traducir(db, str(document_id))

            translate.assert_not_called()
            client.assert_not_called()
            update.assert_called_once_with(db, doc, "english")
            self.assertFalse(result["translated"])
            self.assertEqual(Path(result["english_path"]).read_bytes(), source)

    def test_language_mismatch_keeps_cleaned_status_and_creates_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            document_id = uuid4()
            cleaned = Path(tmp) / "cleaned.txt"
            cleaned.write_text("Este texto está en español.", encoding="utf-8")
            doc = SimpleNamespace(
                id=document_id,
                status="cleaned",
                language="pt",
                original_filename="documento.pdf",
                cleaned_path=str(cleaned),
                english_path=None,
            )
            output_dir = Path(tmp) / "english"
            with (
                patch.object(settings, "STORAGE_ENGLISH", output_dir),
                patch("src.services.documents.DocumentRepo.leer_uno", return_value=doc),
                patch(
                    "src.services.documents.translate_to_english",
                    side_effect=LanguageMismatchError("es no coincide con pt"),
                ),
            ):
                with self.assertRaises(DocumentoError) as raised:
                    DocumentService.traducir(Mock(), str(document_id))

            self.assertEqual(raised.exception.codigo_http, 422)
            self.assertEqual(doc.status, "cleaned")
            self.assertIsNone(doc.english_path)
            self.assertFalse(output_dir.exists())

    def test_llm_receives_segments_and_preserves_document_order(self):
        outputs = {
            "El cacao creció en 2024.": "Cacao grew in 2024.",
            "La agroforestería cubrió 30%.": "Agroforestry covered 30%.",
        }
        client = Mock()

        def create(**kwargs):
            prompt = kwargs["system"]
            self.assertIn("<corpus_context>", prompt)
            self.assertIn("keep the acronym as written", prompt)
            target = json.loads(kwargs["messages"][0]["content"])
            self.assertEqual(target["source_language"], "es")
            self.assertEqual(target["document_title"], "cacao.pdf")
            self.assertTrue(target["document_context_excerpt"].startswith("El cacao"))
            translations = [
                {"segment_id": row["segment_id"], "text": outputs[row["text"]]}
                for row in target["segments"]
            ]
            return SimpleNamespace(
                stop_reason="tool_use",
                content=[SimpleNamespace(
                    type="tool_use",
                    name="submit_translation",
                    input={
                        "source_language_detected": "es",
                        "language_matches_metadata": True,
                        "translations": translations,
                    },
                )],
            )

        client.messages.create.side_effect = create
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "test-key"),
            patch("src.services.translation.get_anthropic_client", return_value=client),
        ):
            result = translate_to_english(
                "El cacao creció en 2024.\n\nLa agroforestería cubrió 30%.",
                "es",
                document_title="cacao.pdf",
            )

        self.assertEqual(result, "Cacao grew in 2024.\n\nAgroforestry covered 30%.")
        client.messages.create.assert_called_once()

    def test_changed_number_is_rejected(self):
        from src.services.translation import Segment, _validate_translation

        with self.assertRaisesRegex(TranslationError, "Cifras"):
            _validate_translation(
                {
                    "source_language_detected": "es",
                    "language_matches_metadata": True,
                    "translations": [{"segment_id": "s00001", "text": "Cacao grew in 2025."}],
                },
                [Segment("s00001", "El cacao creció en 2024.")],
            )

    def test_english_verification_rejects_a_mislabeled_document(self):
        client = Mock()
        client.messages.create.return_value = SimpleNamespace(
            stop_reason="tool_use",
            content=[SimpleNamespace(
                type="tool_use",
                name="submit_translation",
                input={
                    "source_language_detected": "es",
                    "language_matches_metadata": False,
                    "translations": [],
                },
            )],
        )
        with (
            patch.object(settings, "ANTHROPIC_API_KEY", "test-key"),
            patch("src.services.translation.get_anthropic_client", return_value=client),
        ):
            with self.assertRaises(LanguageMismatchError):
                verify_english_language("Este documento está en español.")
        request = client.messages.create.call_args.kwargs
        self.assertIn("Ignore the English corpus context", request["system"])
        self.assertEqual(json.loads(request["messages"][0]["content"])["task"], "verify_language")

    def test_revert_english_removes_only_english_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            document_id = uuid4()
            cleaned = Path(tmp) / "cleaned.txt"
            english = Path(tmp) / "english.txt"
            cleaned.write_text("Fuente", encoding="utf-8")
            english.write_text("Source", encoding="utf-8")
            doc = SimpleNamespace(
                id=document_id,
                status="english",
                cleaned_path=str(cleaned),
                english_path=str(english),
            )
            db = Mock()
            with (
                patch("src.services.documents.DocumentRepo.leer_uno", return_value=doc),
                patch("src.services.documents.DocumentRepo.actualizar_status") as update,
            ):
                DocumentService.revertir(db, str(document_id))
            update.assert_called_once_with(db, doc, "cleaned")
            self.assertIsNone(doc.english_path)
            self.assertFalse(english.exists())
            self.assertTrue(cleaned.exists())

    def test_ner_requires_english_and_revert_restores_english(self):
        document_id = uuid4()
        doc = SimpleNamespace(
            id=document_id,
            status="english",
            original_filename="document.pdf",
            english_path=f"s3/english/{document_id}.txt",
            ner_path=None,
        )
        db = Mock()
        with (
            patch("src.services.documents.DocumentRepo.leer_uno", return_value=doc),
            patch("src.services.documents.Storage.leer", return_value="English text."),
            patch("src.services.documents.extraer_entidades", return_value=[]) as ner,
            patch("src.services.documents.Storage.guardar", return_value=Path("ner.json")),
            patch("src.services.documents.DocumentRepo.actualizar_status") as update,
        ):
            DocumentService.extraer_entidades_de_documento(db, str(document_id))
            ner.assert_called_once()
            self.assertEqual(ner.call_args.args[0], "English text.")
            update.assert_called_once_with(db, doc, "ner")
            doc.status = "ner"
            DocumentService.revertir(db, str(document_id))
            self.assertEqual(update.call_args.args, (db, doc, "english"))

    def test_routes_are_exposed(self):
        app = FastAPI()
        app.include_router(router)
        paths = app.openapi()["paths"]
        self.assertIn("post", paths["/documents/{document_id}/translate"])
        self.assertIn("get", paths["/documents/{document_id}/english"])


if __name__ == "__main__":
    unittest.main()
