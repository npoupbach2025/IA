import json
import unicodedata
from pathlib import Path


class KnowledgeBase:
    """
    Base de connaissances locale utilisée pour enrichir les réponses.

    Cette base de connaissances simplifiée permet d'ajouter du contexte
    Expertisys aux réponses. Elle sert à la maquette, mais ce n'est pas un vrai
    système RAG complet avec embeddings et recherche vectorielle.
    """

    def __init__(self, faq_path=None):
        # Path(__file__) permet de retrouver le dossier du projet même si
        # l'application est lancée depuis un autre répertoire.
        base_dir = Path(__file__).resolve().parents[1]
        self.faq_path = (
            Path(faq_path)
            if faq_path
            else base_dir / "data" / "expertisys_faq.json"
        )
        self.load_error = ""
        self.entries = self._load_entries()

    def _load_entries(self):
        """Charge le fichier JSON contenant les questions/réponses Expertisys."""
        try:
            with self.faq_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            self.load_error = f"Base FAQ introuvable : {self.faq_path}"
        except json.JSONDecodeError:
            self.load_error = f"Format JSON invalide dans : {self.faq_path}"
        return []

    def _normalize_text(self, text):
        """
        Met le texte en minuscules et retire les accents.

        Cela rend la recherche plus tolérante : "sécurité" et "securite" sont
        considérés comme équivalents.
        """
        normalized = unicodedata.normalize("NFD", text.lower())
        return "".join(
            character
            for character in normalized
            if unicodedata.category(character) != "Mn"
        )

    # Recherche dans la FAQ à partir des mots-clés.
    def search(self, user_text):
        """
        Cherche l'entrée FAQ la plus proche du message utilisateur.

        Le principe est simple : on compte combien de mots-clés de chaque entrée
        apparaissent dans le texte utilisateur. L'entrée avec le meilleur score
        sert de contexte. Si aucun mot-clé ne correspond, on retourne None.
        """
        user_text_normalized = self._normalize_text(user_text)
        best_entry = None
        best_score = 0

        for entry in self.entries:
            keywords = entry.get("keywords", [])

            # Score volontairement simple pour rester pédagogique : un mot-clé
            # trouvé dans le message vaut un point.
            score = sum(
                1
                for keyword in keywords
                if self._normalize_text(keyword) in user_text_normalized
            )

            if score > best_score:
                best_score = score
                best_entry = entry

        if not best_entry or best_score <= 0:
            return None

        # Le modèle reçoit un court contexte, pas tout le contenu de la FAQ.
        # Cela évite de lui envoyer un prompt trop long.
        return (
            f"Question proche : {best_entry.get('question')}\n"
            f"Réponse Expertisys : {best_entry.get('answer')}\n"
            f"Catégorie : {best_entry.get('category')}"
        )
