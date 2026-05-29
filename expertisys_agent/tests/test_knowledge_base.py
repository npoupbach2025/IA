import json
import tempfile
import unittest
from pathlib import Path

from src.knowledge_base import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    """Tests de la base de connaissances locale simplifiée."""

    def _create_temp_faq(self, entries):
        temp_dir = tempfile.TemporaryDirectory()
        faq_path = Path(temp_dir.name) / "faq.json"
        faq_path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(temp_dir.cleanup)
        return faq_path

    def test_search_returns_matching_context(self):
        faq_path = self._create_temp_faq(
            [
                {
                    "question": "Comment contacter le support ?",
                    "answer": "Utilisez le portail Expertisys.",
                    "category": "support",
                    "keywords": ["support", "contacter", "portail"],
                },
                {
                    "question": "Comment créer un mot de passe sécurisé ?",
                    "answer": "Utilisez un mot de passe long et unique.",
                    "category": "cybersécurité",
                    "keywords": ["mot de passe", "sécurisé", "unique"],
                },
            ]
        )
        knowledge_base = KnowledgeBase(faq_path)

        result = knowledge_base.search("Je veux contacter le support")

        self.assertIsNotNone(result)
        self.assertIn("Utilisez le portail Expertisys", result)

    def test_search_is_accent_insensitive(self):
        faq_path = self._create_temp_faq(
            [
                {
                    "question": "Comment créer un mot de passe sécurisé ?",
                    "answer": "Utilisez un mot de passe long.",
                    "category": "cybersécurité",
                    "keywords": ["sécurisé"],
                }
            ]
        )
        knowledge_base = KnowledgeBase(faq_path)

        result = knowledge_base.search("mot de passe securise")

        self.assertIsNotNone(result)
        self.assertIn("mot de passe long", result)

    def test_search_returns_none_without_relevant_keyword(self):
        faq_path = self._create_temp_faq(
            [
                {
                    "question": "Comment contacter le support ?",
                    "answer": "Utilisez le portail Expertisys.",
                    "category": "support",
                    "keywords": ["support"],
                }
            ]
        )
        knowledge_base = KnowledgeBase(faq_path)

        self.assertIsNone(knowledge_base.search("recette de cuisine"))

    def test_missing_file_does_not_crash(self):
        knowledge_base = KnowledgeBase(Path("missing_file.json"))

        self.assertEqual(knowledge_base.entries, [])
        self.assertIn("introuvable", knowledge_base.load_error)


if __name__ == "__main__":
    unittest.main()
