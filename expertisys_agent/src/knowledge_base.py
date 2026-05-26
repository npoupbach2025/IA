import json
from pathlib import Path


class KnowledgeBase:
    """
    Base de connaissances locale utilisée pour enrichir les réponses.

    Cette base de connaissances simplifiée permet d'ajouter du contexte
    Expertisys aux réponses. Elle sert à la maquette, mais ce n'est pas un vrai
    système RAG complet avec embeddings et recherche vectorielle.
    """

    def __init__(self, faq_path=None):
        base_dir = Path(__file__).resolve().parents[1]
        self.faq_path = Path(faq_path) if faq_path else base_dir / "data" / "expertisys_faq.json"
        self.entries = self._load_entries()

    def _load_entries(self):
        try:
            with self.faq_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Base FAQ introuvable : {self.faq_path}")
        except json.JSONDecodeError:
            print(f"Format JSON invalide dans : {self.faq_path}")
        return []

    # Recherche dans la FAQ à partir des mots-clés.
    def search(self, user_text):
        user_text_lower = user_text.lower()
        best_entry = None
        best_score = 0

        for entry in self.entries:
            keywords = entry.get("keywords", [])
            score = sum(
                1 for keyword in keywords if keyword.lower() in user_text_lower
            )

            if score > best_score:
                best_score = score
                best_entry = entry

        if not best_entry:
            return None

        return (
            f"Question proche : {best_entry.get('question')}\n"
            f"Réponse Expertisys : {best_entry.get('answer')}\n"
            f"Catégorie : {best_entry.get('category')}"
        )
