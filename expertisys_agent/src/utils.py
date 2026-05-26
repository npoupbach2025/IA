TASK_LABELS = {
    "question_answering": "Répondre à une question",
    "generation": "Générer du texte",
    "rewriting": "Réécrire avec un style donné",
    "completion": "Compléter une idée",
    "cybersecurity": "Conseils cybersécurité",
    "support": "Support client Expertisys",
}


def clean_response(text):
    """Nettoie la réponse pour l'afficher proprement dans l'interface."""
    if not text:
        return ""

    lines = [line.strip() for line in text.strip().splitlines()]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines)


def get_task_label(task_type):
    """Retourne le libellé affiché dans l'interface pour une tâche."""
    return TASK_LABELS.get(task_type, TASK_LABELS["question_answering"])


def get_task_from_label(label):
    """Retrouve l'identifiant interne d'une tâche à partir de son libellé."""
    for task_type, task_label in TASK_LABELS.items():
        if task_label == label:
            return task_type
    return "question_answering"


def get_example_prompts():
    """Retourne des exemples pratiques pour tester rapidement la maquette."""
    return [
        "Comment créer un mot de passe sécurisé ?",
        "Comment reconnaître un email de phishing ?",
        "Je n'arrive pas à me connecter à mon compte.",
        (
            "Réécris ce message dans un style professionnel : j'ai un problème "
            "avec mon accès, ça ne marche pas."
        ),
        (
            "Complète cette idée : pour améliorer la sécurité des postes "
            "utilisateurs, il faut..."
        ),
        "Génère un message court pour confirmer la prise en charge d'un ticket support.",
        "Comment contacter le support Expertisys ?",
    ]
