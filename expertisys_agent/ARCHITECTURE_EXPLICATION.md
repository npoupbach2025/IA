# Explication simple du projet Expertisys

Ce document explique le projet avec des mots simples. L'objectif est de comprendre ce que fait chaque fichier, comment l'application fonctionne, et pourquoi certains choix techniques ont été faits.

## Résumé du projet

Le projet est une maquette d'assistant conversationnel pour l'entreprise fictive Expertisys.

L'utilisateur lance l'application avec :

```bash
python main.py
```

Une fenêtre locale s'ouvre. Dans cette fenêtre, l'utilisateur peut écrire une question ou une demande. L'application détecte automatiquement le type de tâche, puis affiche une réponse générée par le modèle ou par une réponse contrôlée pour certains cas simples.

Le menu de tâche reste présent avec un mode **Automatique** par défaut. Il sert surtout à montrer au jury que les différents modes existent, mais l'utilisateur peut utiliser l'assistant sans toucher à ce menu.

L'application peut servir à tester plusieurs usages :

- répondre à une question ;
- générer un texte professionnel ;
- réécrire un texte avec un style donné ;
- compléter une idée ;
- répondre à des questions de support ;
- donner des conseils simples de cybersécurité.

## Architecture générale

Le projet est organisé en plusieurs fichiers pour éviter de tout mélanger.

```text
expertisys_agent/
│
├── main.py
├── requirements.txt
├── README.md
├── ARCHITECTURE_EXPLICATION.md
│
├── data/
│   └── expertisys_faq.json
│
└── src/
    ├── __init__.py
    ├── model.py
    ├── prompts.py
    ├── knowledge_base.py
    └── utils.py
```

On peut voir l'application comme une chaîne :

```text
Message utilisateur
        ↓
Interface Tkinter dans main.py
        ↓
Détection automatique de la tâche
        ↓
Recherche dans la FAQ locale
        ↓
Construction d'un prompt adapté
        ↓
Envoi au modèle google/flan-t5-small
        ↓
Nettoyage de la réponse
        ↓
Affichage dans la fenêtre
```

## Rôle de chaque fichier

## main.py

`main.py` est le point d'entrée du programme.

C'est le fichier lancé par la commande :

```bash
python main.py
```

Il sert à créer l'interface graphique avec Tkinter. C'est lui qui affiche :

- la fenêtre principale ;
- le titre de l'application ;
- la zone de conversation ;
- le champ de saisie ;
- le bouton Envoyer ;
- le bouton Effacer la conversation ;
- le menu de tâche en mode automatique par défaut ;
- le menu de style pour les reformulations ;
- la colonne de droite avec les exemples de prompts.

Il ne contient pas directement toute l'intelligence de l'application. Il appelle les autres fichiers du dossier `src/`.

Quand l'utilisateur clique sur Envoyer, `main.py` fait plusieurs actions :

1. il récupère le texte écrit par l'utilisateur ;
2. il détecte automatiquement la tâche à effectuer ;
3. il cherche une information utile dans la FAQ ;
4. il demande à `prompts.py` de créer une consigne pour le modèle ;
5. il demande à `model.py` de générer une réponse si nécessaire ;
6. il nettoie la réponse avec `utils.py` ;
7. il affiche la réponse dans la zone de chat.

Le fichier utilise aussi un `thread`. Cela permet de garder la fenêtre active pendant que le modèle réfléchit. Sans cela, l'application pourrait sembler bloquée pendant la génération.

## requirements.txt

`requirements.txt` contient la liste des bibliothèques Python nécessaires.

Il permet d'installer facilement les dépendances avec :

```bash
pip install -r requirements.txt
```

Le fichier contient :

- `transformers` : pour charger le modèle Hugging Face ;
- `torch` : pour faire fonctionner le modèle avec PyTorch ;
- `sentencepiece` : nécessaire pour certains tokenizers ;
- `accelerate` : utile pour charger et exécuter les modèles plus facilement.

Il ne contient pas Streamlit, car le projet utilise Tkinter.

## README.md

`README.md` est le document de présentation rapide du projet.

Il explique :

- le contexte ;
- l'objectif ;
- les fonctionnalités ;
- le modèle utilisé ;
- les commandes d'installation ;
- la commande de lancement ;
- les limites du prototype.

C'est généralement le premier fichier qu'une personne lit quand elle découvre un projet.

## ARCHITECTURE_EXPLICATION.md

Ce fichier est le document que vous êtes en train de lire.

Il va plus loin que le README. Il explique l'organisation du code, le rôle de chaque fichier et le fonctionnement général avec un vocabulaire plus accessible.

## data/expertisys_faq.json

Ce fichier contient la base de connaissances locale.

Il s'agit d'un fichier JSON avec 10 000 entrées fictives. Chaque entrée contient :

- `question` : une question possible d'un client ;
- `answer` : la réponse associée ;
- `category` : la catégorie de la question ;
- `keywords` : des mots-clés utilisés pour retrouver cette entrée.

Exemple simplifié :

```json
{
  "question": "Comment réinitialiser mon mot de passe ?",
  "answer": "Depuis la page de connexion Expertisys, cliquez sur Mot de passe oublié...",
  "category": "mot de passe",
  "keywords": ["réinitialiser", "mot de passe", "oublié"]
}
```

Cette base permet à l'assistant d'ajouter du contexte Expertisys avant d'interroger le modèle.

Ce n'est pas un vrai système RAG complet. Un vrai RAG utiliserait souvent une base vectorielle, des embeddings et une recherche sémantique. Ici, la recherche est volontairement plus simple pour rester compréhensible.

## src/__init__.py

Ce fichier indique que le dossier `src` est un module Python.

Il est presque vide, mais il permet d'importer proprement les fichiers du dossier `src`.

Exemple :

```python
from src.model import ExpertisysLLM
```

## src/model.py

`model.py` gère le modèle d'intelligence artificielle.

Il contient la classe `ExpertisysLLM`.

Cette classe fait trois choses principales :

1. charger le tokenizer ;
2. charger le modèle ;
3. générer une réponse à partir d'un prompt.

Le modèle utilisé est :

```text
google/flan-t5-small
```

Le modèle est chargé une seule fois au démarrage. C'est important, car charger un modèle peut être long. Si on le rechargeait à chaque message, l'application serait beaucoup trop lente.

## Qu'est-ce qu'un tokenizer ?

Un modèle ne comprend pas directement le texte comme un humain.

Le tokenizer transforme une phrase en nombres que le modèle peut traiter.

Exemple simplifié :

```text
"Bonjour client"
```

devient une suite d'identifiants numériques.

Après la génération, le tokenizer fait aussi l'opération inverse : il transforme la réponse numérique du modèle en texte lisible.

## Pourquoi google/flan-t5-small ?

`google/flan-t5-small` a été choisi pour une maquette parce qu'il est :

- relativement léger ;
- simple à utiliser avec Hugging Face Transformers ;
- adapté aux consignes courtes ;
- suffisant pour tester une interface et une logique de prototype ;
- plus facile à exécuter localement qu'un grand modèle.

Ce n'est pas le modèle le plus puissant. Pour une vraie application en production, il faudrait comparer plusieurs modèles, mesurer la qualité des réponses, vérifier les performances et réfléchir à la sécurité des données.

## src/prompts.py

`prompts.py` construit les consignes envoyées au modèle.

Un prompt est une instruction donnée au modèle.

Exemple :

```text
Réponds clairement à la question suivante pour un client Expertisys : ...
```

Le fichier contient plusieurs templates de prompts pour chaque type de tâche :

- question-réponse ;
- génération ;
- réécriture ;
- complétion ;
- cybersécurité ;
- support client.

Le but est de guider le modèle. Si on donne une consigne vague, le modèle risque de répondre de manière trop générale. Si on donne une consigne claire, la réponse est souvent plus utile.

Le fichier ajoute aussi le contexte trouvé dans la FAQ quand il existe.

## src/knowledge_base.py

`knowledge_base.py` charge et interroge la base de connaissances locale.

Il contient la classe `KnowledgeBase`.

Cette classe :

1. ouvre le fichier `data/expertisys_faq.json` ;
2. lit les 10 000 entrées ;
3. compare le message utilisateur avec les mots-clés ;
4. retourne la réponse la plus proche si elle trouve une correspondance ;
5. retourne `None` si rien ne correspond.

La recherche est simple. Elle ne comprend pas vraiment le sens profond des phrases. Elle regarde surtout si des mots-clés apparaissent dans le message.

Pour une maquette, c'est suffisant pour montrer le principe d'une base de connaissances.

## src/utils.py

`utils.py` contient des petites fonctions utiles utilisées par plusieurs parties du projet.

Il contient notamment :

- `clean_response()` : nettoie les réponses du modèle ;
- `detect_task_type()` : choisit automatiquement la tâche selon le message ;
- `get_task_label()` : transforme un nom technique en libellé visible ;
- `get_task_from_label()` : transforme un libellé visible en nom technique ;
- `get_example_prompts()` : fournit les exemples de prompts affichés dans l'interface.

Ces fonctions sont séparées du reste pour éviter de surcharger `main.py`.

## Fonctionnement détaillé quand on envoie un message

Quand l'utilisateur écrit :

```text
Comment créer un mot de passe sécurisé ?
```

voici ce qui se passe :

1. `main.py` récupère le texte dans la zone de saisie.
2. `KnowledgeBase.search()` cherche des mots-clés dans la FAQ.
3. Une entrée proche est trouvée dans `expertisys_faq.json`.
4. `build_prompt()` construit une consigne complète pour le modèle.
5. Le contexte FAQ est ajouté au prompt.
6. `ExpertisysLLM.generate()` envoie le prompt au modèle.
7. Le modèle génère une réponse.
8. `clean_response()` nettoie le texte.
9. `main.py` affiche la réponse dans l'historique.

## Pourquoi utiliser Tkinter ?

Tkinter est inclus avec Python dans la plupart des installations.

Il permet de créer une vraie fenêtre locale sans navigateur web et sans framework externe comme Streamlit, React ou FastAPI.

Pour une maquette simple, Tkinter est pratique car :

- il reste 100 % Python ;
- il ne nécessite pas de serveur web ;
- il permet de lancer une application locale facilement ;
- il suffit de faire `python main.py`.

## Pourquoi utiliser une FAQ locale ?

Le modèle seul ne connaît pas forcément les informations internes d'Expertisys.

La FAQ locale sert donc à donner un contexte avant la génération.

Par exemple, si l'utilisateur demande comment contacter le support, la base peut fournir une réponse Expertisys au modèle. Le modèle peut ensuite formuler une réponse plus naturelle.

## Pourquoi limiter la longueur des réponses ?

Dans `model.py`, la génération est limitée à environ 120 tokens.

Cela évite :

- les réponses trop longues ;
- les textes hors sujet ;
- les temps de génération trop importants ;
- une interface difficile à lire.

Pour un assistant support, une réponse courte et claire est souvent plus utile qu'un long paragraphe.

## Limites importantes

Cette application est une maquette.

Elle ne doit pas être utilisée comme un vrai support client sans améliorations.

Ses principales limites sont :

- la FAQ est fictive ;
- la recherche par mots-clés est simple ;
- le modèle peut se tromper ;
- il n'y a pas d'authentification utilisateur ;
- il n'y a pas de connexion à un vrai outil de ticketing ;
- il n'y a pas de contrôle avancé des réponses ;
- il ne faut pas y mettre de données sensibles.

## Ce qu'il faudrait améliorer pour une vraie version

Pour passer d'une maquette à une version plus sérieuse, il faudrait ajouter :

- une vraie base documentaire ;
- une recherche sémantique avec embeddings ;
- une validation des réponses ;
- une gestion des utilisateurs ;
- une connexion au support Expertisys ;
- des logs ;
- des tests automatisés ;
- une politique de sécurité des données ;
- un modèle plus performant si nécessaire.

## Conclusion

Le projet montre comment construire un assistant conversationnel local en Python.

L'interface Tkinter permet de discuter avec l'assistant, la FAQ locale ajoute du contexte Expertisys, les prompts guident le modèle, et `google/flan-t5-small` génère les réponses.

L'ensemble reste volontairement simple, lisible et pédagogique pour pouvoir être présenté et expliqué facilement.
