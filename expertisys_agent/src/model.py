from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class ExpertisysLLM:
    """Gestion du modèle Hugging Face utilisé par la maquette."""

    def __init__(self):
        # Le nom du modèle est isolé dans un attribut pour pouvoir le remplacer
        # facilement plus tard par un autre modèle compatible.
        self.model_name = "google/flan-t5-small"
        self.tokenizer = None
        self.model = None
        self.is_ready = False
        self.load_error = ""

        # Le modèle est chargé une seule fois au démarrage pour éviter de
        # ralentir chaque message.
        self._load_model()

    def _load_model(self):
        """
        Télécharge si nécessaire et charge le tokenizer puis le modèle.

        Cette étape peut être lente au premier lancement, mais elle n'est faite
        qu'une seule fois. Ensuite, les générations réutilisent les mêmes objets.
        """
        try:
            # google/flan-t5-small est utilisé car il est léger, gratuit à tester
            # localement, et adapté aux tâches simples de génération guidée.
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            # Le tokenizer transforme le texte en identifiants numériques que le
            # modèle peut comprendre, puis reconvertit la sortie en texte lisible.
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.is_ready = True
        except Exception as exc:
            # En cas d'erreur, l'application continue de s'ouvrir et affiche un
            # message clair au lieu de fermer brutalement la fenêtre.
            self.load_error = (
                "Le modèle google/flan-t5-small n'a pas pu être chargé. "
                "Vérifiez votre connexion Internet lors du premier lancement, "
                "puis réessayez. "
                f"Détail technique : {exc}"
            )
            print(self.load_error)

    # Génération de réponse à partir du prompt construit pour la tâche.
    def generate(self, prompt):
        """
        Génère une réponse textuelle à partir du prompt.

        La méthode retourne toujours une chaîne de caractères, même si une
        erreur se produit, afin que l'interface puisse afficher un message
        compréhensible à l'utilisateur.
        """
        if not self.is_ready:
            return self.load_error

        try:
            # Le prompt est converti en tenseurs PyTorch, format attendu par le
            # modèle Transformers.
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)

            # La longueur est limitée pour garder des réponses courtes, lisibles
            # et adaptées à une interface de support client.
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=160,
                do_sample=False,
                num_beams=4,
                no_repeat_ngram_size=3,
                repetition_penalty=1.8,
                early_stopping=True,
            )

            # La sortie numérique du modèle est reconvertie en texte lisible.
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if not response.strip():
                return (
                    "Je n'ai pas pu générer une réponse fiable. Merci de reformuler "
                    "ou de contacter le support Expertisys."
                )

            return response
        except Exception as exc:
            return (
                "Une erreur est survenue pendant la génération de la réponse. "
                "Merci de reformuler ou de contacter le support Expertisys. "
                f"Détail technique : {exc}"
            )
