import json
import unittest
from pathlib import Path


class FaqDataTests(unittest.TestCase):
    """Tests d'intégrité du fichier JSON de FAQ."""

    @classmethod
    def setUpClass(cls):
        project_root = Path(__file__).resolve().parents[1]
        faq_path = project_root / "data" / "expertisys_faq.json"
        cls.entries = json.loads(faq_path.read_text(encoding="utf-8"))

    def test_faq_contains_enough_entries(self):
        self.assertGreaterEqual(len(self.entries), 15)

    def test_all_entries_have_required_fields(self):
        required_fields = {"question", "answer", "category", "keywords"}

        for index, entry in enumerate(self.entries):
            with self.subTest(index=index):
                self.assertTrue(required_fields.issubset(entry))
                self.assertIsInstance(entry["keywords"], list)

    def test_required_categories_are_present(self):
        categories = {entry["category"] for entry in self.entries}
        required_categories = {
            "support",
            "cybersécurité",
            "compte utilisateur",
            "mot de passe",
            "contact",
            "bonnes pratiques",
        }

        self.assertTrue(required_categories.issubset(categories))


if __name__ == "__main__":
    unittest.main()
