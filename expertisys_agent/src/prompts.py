def build_prompt(task_type, user_text, style=None, context=None):
    """
    Construit le prompt envoyé au modèle selon la tâche choisie.

    Cette fonction adapte le prompt selon la tâche choisie par l'utilisateur.
    Le contexte FAQ, s'il existe, est ajouté pour orienter la réponse vers les
    informations propres à Expertisys.
    """
    # Chaque tâche utilise une consigne différente. C'est important car le même
    # modèle peut se comporter différemment selon la formulation du prompt.
    prompts = {
        "question_answering": (
            "Réponds clairement à la question suivante pour un client Expertisys. "
            "Si tu ne sais pas, dis qu'il faut contacter le support : {user_text}"
        ),
        "generation": (
            "Génère un court texte professionnel pour Expertisys sur le sujet "
            "suivant : {user_text}"
        ),
        "rewriting": (
            "Réécris le texte suivant dans un style {style}, clair et "
            "professionnel : {user_text}"
        ),
        "completion": (
            "Complète l'idée suivante de manière claire, utile et "
            "professionnelle : {user_text}"
        ),
        "cybersecurity": (
            "Donne une réponse courte, claire et prudente sur la cybersécurité. "
            "Ne donne pas d'instructions dangereuses. Question : {user_text}"
        ),
        "support": (
            "Tu es l'assistant support de l'entreprise Expertisys. Réponds au "
            "client de manière polie, utile et concise : {user_text}"
        ),
    }

    # Si un type de tâche inconnu arrive, on utilise par sécurité le mode
    # question-réponse au lieu de faire planter l'application.
    selected_prompt = prompts.get(task_type, prompts["question_answering"])

    # Les valeurs sont insérées ici, juste avant l'envoi au modèle.
    # Pour la réécriture, le style choisi par l'utilisateur est aussi intégré.
    prompt = selected_prompt.format(
        user_text=user_text.strip(),
        style=style or "professionnel",
    )

    if context:
        # Le contexte FAQ est placé avant la consigne pour que le modèle le voie
        # comme une information utile à prendre en compte dans sa réponse.
        prompt = (
            f"Contexte utile provenant de la base Expertisys : {context}\n\n"
            f"{prompt}"
        )

    return prompt
