import re


TASK_LABELS = {
    # Dictionnaire central entre les identifiants utilisés par le code et les
    # libellés affichés dans l'interface Tkinter.
    "question_answering": "Répondre à une question",
    "generation": "Générer du texte",
    "rewriting": "Réécrire avec un style donné",
    "completion": "Compléter une idée",
    "cybersecurity": "Conseils cybersécurité",
    "support": "Support client Expertisys",
}


def clean_response(text):
    """
    Nettoie la réponse pour l'afficher proprement dans l'interface.

    Les modèles peuvent parfois produire des espaces ou lignes vides inutiles.
    Cette fonction rend simplement le texte plus lisible dans les bulles de chat.
    """
    if not text:
        return ""

    # On supprime les espaces autour de chaque ligne puis on retire les lignes
    # entièrement vides.
    lines = [line.strip() for line in text.strip().splitlines()]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines)


def is_email_request(user_text):
    """
    Détecte si l'utilisateur demande la rédaction d'un e-mail.

    Le petit modèle utilisé dans la maquette peut parfois recopier le prompt au
    lieu de rédiger le mail. Cette détection permet de traiter ce cas fréquent
    avec une réponse contrôlée et beaucoup plus propre.
    """
    text = user_text.lower()
    writing_words = [
        "écris",
        "ecris",
        "écrit",
        "ecrit",
        "écrire",
        "ecrire",
        "rédige",
        "redige",
        "rédiger",
        "rediger",
        "prépare",
        "prepare",
        "faire",
        "fais",
    ]
    email_words = ["mail", "email", "e-mail", "courriel"]
    return any(word in text for word in writing_words) and any(
        word in text for word in email_words
    )


def _extract_email_purpose(user_text):
    """
    Récupère le sujet principal du mail demandé.

    Exemple : "écris un mail pour dire que mon compte est bloqué" devient
    "mon compte est bloqué".
    """
    text = user_text.strip()
    patterns = [
        r"pour dire que\s+(.+)",
        r"pour expliquer que\s+(.+)",
        r"pour indiquer que\s+(.+)",
        r"concernant\s+(.+)",
        r"au sujet de\s+(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,*")

    return "j'ai besoin d'assistance concernant mon accès"


def build_email_response(user_text):
    """
    Génère directement un e-mail simple en français.

    Ce n'est pas un remplacement du LLM pour toute l'application. C'est un
    garde-fou pour un cas très courant où un petit modèle peut produire une
    sortie peu présentable.
    """
    purpose = _extract_email_purpose(user_text)
    purpose_lower = purpose.lower()

    if "compte" in purpose_lower and (
        "bloqué" in purpose_lower or "bloque" in purpose_lower
    ):
        subject = "Demande d'assistance - compte bloqué"
        main_sentence = "mon compte est actuellement bloqué et je ne parviens plus à y accéder"
    else:
        subject = "Demande d'assistance"
        main_sentence = purpose

    return (
        f"Objet : {subject}\n\n"
        "Bonjour,\n\n"
        f"Je me permets de vous contacter car {main_sentence}.\n\n"
        "Pouvez-vous m'aider à résoudre ce problème ou m'indiquer les étapes à suivre ? "
        "Je reste disponible pour vous transmettre toute information complémentaire "
        "nécessaire au traitement de ma demande.\n\n"
        "Cordialement,\n"
        "[Votre nom]"
    )


def get_task_label(task_type):
    """Retourne le libellé affiché dans l'interface pour une tâche."""
    return TASK_LABELS.get(task_type, TASK_LABELS["question_answering"])


def get_task_from_label(label):
    """Retrouve l'identifiant interne d'une tâche à partir de son libellé."""
    # Tkinter manipule le texte visible par l'utilisateur. Le reste du code
    # préfère utiliser des identifiants courts comme "support" ou "completion".
    for task_type, task_label in TASK_LABELS.items():
        if task_label == label:
            return task_type
    return "question_answering"


def get_example_prompts():
    """
    Retourne des exemples pratiques pour tester rapidement la maquette.

    Ces exemples sont affichés sous forme de boutons dans la colonne de droite.
    """
    return [
        "Comment créer un mot de passe sécurisé ?",
        "Comment reconnaître un email de phishing ?",
        "Je n'arrive pas à me connecter à mon compte.",
        "Que faire si mon compte Expertisys est verrouillé ?",
        "Pourquoi activer la double authentification ?",
        "Comment suivre l'état de mon ticket support ?",
        "Comment signaler un incident de sécurité ?",
        "Que faire si j'ai reçu un email suspect ?",
        "Comment vérifier qu'un site est légitime ?",
        "Quelles informations fournir au support Expertisys ?",
        "Comment modifier mon adresse e-mail de contact ?",
        "Comment demander une assistance prioritaire ?",
        "Comment éviter de partager des données sensibles ?",
        "Comment sécuriser mon poste de travail ?",
        "Que faire si j'ai téléchargé une pièce jointe suspecte ?",
        "Comment contacter le support Expertisys ?",
        "Comment créer un compte utilisateur Expertisys ?",
        "Je n'ai pas reçu l'e-mail d'activation de mon compte.",
        "Le portail client affiche une erreur, que dois-je faire ?",
        "Je veux expliquer simplement ce qu'est le phishing.",
        "Donne trois bonnes pratiques pour protéger un ordinateur professionnel.",
        "Donne une réponse courte à un client qui a oublié son mot de passe.",
        "Génère un message d'accueil pour l'assistant IA Expertisys.",
        "Génère un message court pour confirmer la prise en charge d'un ticket support.",
        "Génère un texte professionnel pour présenter le support Expertisys.",
        "Génère un message de prévention sur les mots de passe faibles.",
        "Génère une réponse polie pour demander plus d'informations à un client.",
        "Génère un message pour informer qu'un ticket est en cours d'analyse.",
        "Génère une courte annonce interne sur la cybersécurité.",
        "Génère une réponse pour rassurer un client après l'ouverture d'un ticket.",
        (
            "Réécris ce message dans un style professionnel : j'ai un problème "
            "avec mon accès, ça ne marche pas."
        ),
        (
            "Réécris ce message dans un style formel : salut, mon compte est "
            "bloqué et j'ai besoin d'aide vite."
        ),
        (
            "Réécris ce message dans un style simple : veuillez procéder à la "
            "réinitialisation de vos identifiants d'accès."
        ),
        (
            "Réécris ce message dans un style amical : votre demande a bien été "
            "reçue par notre support."
        ),
        (
            "Réécris ce message dans un style synthétique : nous avons identifié "
            "un incident de connexion et nos équipes vérifient la situation."
        ),
        (
            "Complète cette idée : pour améliorer la sécurité des postes "
            "utilisateurs, il faut..."
        ),
        (
            "Complète cette idée : un bon assistant support doit aider le client "
            "à..."
        ),
        (
            "Complète cette idée : avant de cliquer sur un lien reçu par e-mail, "
            "il est important de..."
        ),
        (
            "Complète cette idée : pour réduire les risques liés aux mots de "
            "passe, une entreprise peut..."
        ),
        (
            "Complète cette idée : lorsqu'un incident de sécurité est suspecté, "
            "le premier réflexe est de..."
        ),
        "Réponds à ce client : je ne comprends pas pourquoi mon accès ne fonctionne plus.",
        "Réponds à ce client : pouvez-vous me dire où trouver mes tickets ouverts ?",
        "Réponds à ce client : je pense avoir cliqué sur un lien frauduleux.",
        "Réponds à ce client : mon mot de passe a peut-être été compromis.",
        "Réponds à ce client : je souhaite changer mes coordonnées de contact.",
    ]
