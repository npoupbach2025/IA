"""
Construction des prompts envoyés au modèle LLM.

Un prompt est la consigne donnée au modèle. Dans cette maquette, l'utilisateur
choisit une tâche dans l'interface, puis ce fichier transforme son message en
instruction claire pour google/flan-t5-small.
"""


# Cette règle est ajoutée à tous les prompts pour éviter que le modèle réponde
# en anglais. Le modèle reste imparfait, mais une consigne explicite améliore
# fortement la cohérence linguistique des réponses.
FRENCH_ONLY_INSTRUCTION = (
    "Règle obligatoire : réponds uniquement en français. "
    "N'utilise pas l'anglais, sauf si l'utilisateur demande explicitement une traduction."
)


# Plusieurs formulations sont proposées pour chaque tâche.
# Cela permet de tester différents comportements sans changer le reste du code.
PROMPT_TEMPLATES = {
    "question_answering": [
        (
            "Réponds clairement à la question suivante pour un client Expertisys. "
            "Si tu ne sais pas, dis qu'il faut contacter le support : {user_text}"
        ),
        (
            "Tu es un assistant Expertisys. Donne une réponse simple, utile et "
            "compréhensible à cette question client : {user_text}"
        ),
        (
            "Réponds comme un conseiller Expertisys. Sois précis, rassurant et "
            "évite les détails inutiles. Question : {user_text}"
        ),
        (
            "Explique la réponse à un client non technique d'Expertisys. Utilise "
            "un ton professionnel et accessible : {user_text}"
        ),
        (
            "Analyse la demande suivante et réponds avec une solution courte. Si "
            "l'information manque, recommande de contacter le support Expertisys : {user_text}"
        ),
        (
            "Fournis une réponse fiable pour Expertisys en distinguant ce qui est "
            "certain de ce qui doit être confirmé par le support : {user_text}"
        ),
    ],
    "generation": [
        (
            "Génère un court texte professionnel pour Expertisys sur le sujet "
            "suivant : {user_text}"
        ),
        (
            "Rédige un message clair et professionnel pour Expertisys à partir de "
            "ce thème : {user_text}"
        ),
        (
            "Écris un texte bref, sérieux et présentable devant un client "
            "Expertisys sur le sujet : {user_text}"
        ),
        (
            "Crée un paragraphe de communication interne ou client pour Expertisys. "
            "Le texte doit être fluide et utile : {user_text}"
        ),
        (
            "Propose une formulation professionnelle, courte et adaptée à une "
            "entreprise de services numériques : {user_text}"
        ),
        (
            "Rédige un message Expertisys avec un ton clair, poli et orienté "
            "solution. Sujet : {user_text}"
        ),
    ],
    "rewriting": [
        (
            "Réécris le texte suivant dans un style {style}, clair et "
            "professionnel : {user_text}"
        ),
        (
            "Reformule ce message avec un style {style}. Garde le sens initial, "
            "mais rends le texte plus propre : {user_text}"
        ),
        (
            "Améliore la formulation suivante dans un style {style}, sans ajouter "
            "d'informations inventées : {user_text}"
        ),
        (
            "Transforme ce texte en message {style}, adapté à un échange client "
            "Expertisys : {user_text}"
        ),
        (
            "Réécris ce contenu pour qu'il soit plus lisible, plus correct et "
            "plus {style} : {user_text}"
        ),
        (
            "Propose une version {style} et professionnelle du texte suivant. "
            "Conserve l'idée principale : {user_text}"
        ),
    ],
    "completion": [
        (
            "Complète l'idée suivante de manière claire, utile et "
            "professionnelle : {user_text}"
        ),
        (
            "Continue cette idée avec quelques phrases cohérentes et adaptées à "
            "Expertisys : {user_text}"
        ),
        (
            "Développe la proposition suivante en restant concret, simple et "
            "orienté action : {user_text}"
        ),
        (
            "Ajoute une suite logique et professionnelle à cette idée. Ne pars pas "
            "dans un sujet différent : {user_text}"
        ),
        (
            "Complète ce début de réponse pour en faire un message utile à un "
            "client Expertisys : {user_text}"
        ),
        (
            "Prolonge cette idée avec des conseils ou étapes réalistes, en gardant "
            "un ton clair : {user_text}"
        ),
    ],
    "cybersecurity": [
        (
            "Donne une réponse courte, claire et prudente sur la cybersécurité. "
            "Ne donne pas d'instructions dangereuses. Question : {user_text}"
        ),
        (
            "Réponds à cette question cybersécurité avec des conseils simples et "
            "défensifs uniquement : {user_text}"
        ),
        (
            "Explique la bonne pratique de sécurité adaptée à cette situation. "
            "Reste prudent et recommande le support en cas de doute : {user_text}"
        ),
        (
            "Tu aides un client Expertisys à comprendre un risque cyber. Donne une "
            "réponse accessible, sans procédure offensive : {user_text}"
        ),
        (
            "Fournis une recommandation cybersécurité courte, concrète et sans "
            "action dangereuse : {user_text}"
        ),
        (
            "Réponds comme un assistant de prévention cyber. Priorise la sécurité, "
            "la prudence et le signalement des incidents : {user_text}"
        ),
    ],
    "support": [
        (
            "Tu es l'assistant support de l'entreprise Expertisys. Réponds au "
            "client de manière polie, utile et concise : {user_text}"
        ),
        (
            "Réponds comme un agent support Expertisys. Propose une première "
            "étape claire et indique quand contacter le support : {user_text}"
        ),
        (
            "Aide le client Expertisys avec une réponse courte, calme et orientée "
            "résolution : {user_text}"
        ),
        (
            "Traite cette demande support avec un ton professionnel. Donne une "
            "action simple à effectuer : {user_text}"
        ),
        (
            "Formule une réponse de support client Expertisys. Sois poli, précis "
            "et évite les promesses non vérifiées : {user_text}"
        ),
        (
            "Réponds à ce problème client comme dans un portail support. Demande "
            "les informations utiles si nécessaire : {user_text}"
        ),
    ],
}


def _select_template(task_type, user_text):
    """
    Sélectionne une formulation de prompt pour la tâche demandée.

    On évite le hasard pur pour garder un comportement stable : le même message
    utilisateur choisira toujours le même template. C'est plus simple à tester
    et plus propre pour une démonstration.
    """
    templates = PROMPT_TEMPLATES.get(
        task_type,
        PROMPT_TEMPLATES["question_answering"],
    )
    text_score = sum(ord(character) for character in user_text)
    return templates[text_score % len(templates)]


def build_prompt(task_type, user_text, style=None, context=None):
    """
    Construit le prompt complet envoyé au modèle.

    Cette fonction adapte le prompt selon la tâche choisie par l'utilisateur.
    Le contexte FAQ, s'il existe, est ajouté pour orienter la réponse vers les
    informations propres à Expertisys.
    """
    # La consigne de base dépend du type de tâche : support, cybersécurité,
    # génération, réécriture, etc.
    selected_prompt = _select_template(task_type, user_text)

    # Les valeurs sont insérées ici, juste avant l'envoi au modèle.
    # Pour la réécriture, le style choisi par l'utilisateur est aussi intégré.
    prompt = selected_prompt.format(
        user_text=user_text.strip(),
        style=style or "professionnel",
    )

    # La règle de langue est placée dans chaque prompt final pour que toutes les
    # tâches de l'application produisent une réponse en français.
    prompt = f"{FRENCH_ONLY_INSTRUCTION}\n\n{prompt}"

    if context:
        # Le contexte FAQ est placé avant la consigne pour que le modèle le voie
        # comme une information utile à prendre en compte dans sa réponse.
        prompt = (
            f"Contexte utile provenant de la base Expertisys : {context}\n\n"
            f"{prompt}"
        )

    return prompt
