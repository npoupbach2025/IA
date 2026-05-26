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


def response_needs_french_fallback(text):
    """
    Repère les réponses qui ne respectent pas la contrainte "français uniquement".

    Le modèle peut parfois traduire une partie du prompt ou répondre en anglais.
    Cette fonction détecte quelques marqueurs fréquents pour éviter d'afficher
    une réponse peu présentable dans l'application.
    """
    if not text:
        return True

    lowered = text.lower()
    english_markers = [
        "what should",
        "if i want",
        "recommendations",
        "change immediately",
        "the user",
        "user asks",
        "write directly",
        "question close",
        "what must be",
        "must be confirmed",
        "may tu me dire",
        "changing my",
        "contact expertisys to verify your identity",
    ]
    return any(marker in lowered for marker in english_markers)


def extract_answer_from_context(context):
    """
    Extrait la réponse Expertisys depuis le contexte de FAQ.

    Le contexte est construit dans knowledge_base.py. Cette fonction permet de
    récupérer uniquement la partie utile si le modèle produit une mauvaise
    réponse et qu'il faut afficher une réponse française contrôlée.
    """
    if not context or "Réponse Expertisys :" not in context:
        return None

    answer_part = context.split("Réponse Expertisys :", 1)[1]
    answer = answer_part.split("Catégorie :", 1)[0].strip()
    return answer or None


def build_french_fallback_response(user_text, context=None):
    """
    Construit une réponse de secours entièrement en français.

    Cette réponse est utilisée quand le modèle répond en anglais ou recopie le
    prompt. Elle privilégie la FAQ si une information pertinente a été trouvée.
    """
    faq_answer = extract_answer_from_context(context)
    if faq_answer:
        return f"D'après la base Expertisys : {faq_answer}"

    return (
        "Je peux vous aider, mais je n'ai pas trouvé de réponse suffisamment "
        "fiable dans la base Expertisys. Merci de reformuler votre demande ou "
        "de contacter le support Expertisys pour une vérification."
    )


def is_password_request(user_text):
    """
    Détecte une demande courante liée au changement de mot de passe.

    Ce cas revient souvent en support. On le traite directement pour éviter une
    réponse en anglais ou une réponse trop approximative du petit modèle.
    """
    text = user_text.lower()
    password_words = ["mot de passe", "password"]
    action_words = [
        "changer",
        "modifier",
        "réinitialiser",
        "reinitialiser",
        "oublié",
        "oublie",
        "perdu",
    ]
    return any(word in text for word in password_words) and any(
        word in text for word in action_words
    )


def build_password_response():
    """Retourne une réponse support simple pour le changement de mot de passe."""
    return (
        "Pour changer ou réinitialiser votre mot de passe Expertisys, allez sur "
        "la page de connexion puis cliquez sur \"Mot de passe oublié\". Saisissez "
        "votre adresse e-mail professionnelle et suivez le lien reçu par e-mail.\n\n"
        "Si vous ne recevez pas le message ou si votre compte semble bloqué, "
        "contactez le support Expertisys afin qu'il vérifie votre accès."
    )


def detect_task_type(user_text):
    """
    Détecte automatiquement la tâche à utiliser selon le message utilisateur.

    Le but est que l'utilisateur écrive naturellement, sans devoir choisir une
    tâche dans un menu. L'ordre des règles est important : on teste d'abord les
    intentions très spécifiques, puis les cas plus généraux.
    """
    text = user_text.lower()

    rewriting_keywords = [
        "réécris",
        "reecris",
        "reformule",
        "corrige",
        "améliore ce texte",
        "ameliore ce texte",
        "style professionnel",
        "style formel",
        "style simple",
        "style amical",
        "style synthétique",
        "style synthetique",
    ]
    completion_keywords = [
        "complète",
        "complete",
        "continue",
        "termine",
        "poursuis",
        "développe cette idée",
        "developpe cette idee",
        "pour améliorer",
        "pour ameliorer",
    ]
    cybersecurity_keywords = [
        "cybersécurité",
        "cybersecurite",
        "sécurité",
        "securite",
        "phishing",
        "hameçonnage",
        "hameconnage",
        "email suspect",
        "pièce jointe",
        "piece jointe",
        "malware",
        "virus",
        "antivirus",
        "double authentification",
        "2fa",
        "mfa",
        "données sensibles",
        "donnees sensibles",
        "site légitime",
        "site legitime",
        "incident de sécurité",
        "incident de securite",
    ]
    support_keywords = [
        "support",
        "ticket",
        "compte bloqué",
        "compte bloque",
        "connexion",
        "connecter",
        "accès",
        "acces",
        "portail",
        "assistance",
        "contacter",
        "activation",
        "identifiant",
        "adresse e-mail",
        "adresse email",
    ]
    generation_keywords = [
        "génère",
        "genere",
        "écris",
        "ecris",
        "écrit",
        "ecrit",
        "rédige",
        "redige",
        "prépare",
        "prepare",
        "crée un texte",
        "cree un texte",
        "message court",
        "annonce",
        "mail",
        "email",
        "e-mail",
    ]

    if is_email_request(text):
        return "generation"
    if is_password_request(text):
        return "support"
    if any(keyword in text for keyword in rewriting_keywords):
        return "rewriting"
    if any(keyword in text for keyword in completion_keywords):
        return "completion"
    if any(keyword in text for keyword in cybersecurity_keywords):
        return "cybersecurity"
    if any(keyword in text for keyword in support_keywords):
        return "support"
    if any(keyword in text for keyword in generation_keywords):
        return "generation"

    return "question_answering"


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
