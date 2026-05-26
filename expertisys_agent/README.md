# Assistant IA Expertisys

## Contexte

Expertisys souhaite étudier l'utilisation d'un assistant conversationnel pour aider ses clients. Cette maquette locale permet de tester un agent capable de répondre à des questions fréquentes, d'aider au support client et de donner des conseils simples en cybersécurité.

Le projet est volontairement simple : il utilise uniquement Python, Tkinter pour l'interface graphique, Hugging Face Transformers pour le modèle et PyTorch pour l'exécution.

## Objectif

L'objectif est de fournir une application locale qui s'ouvre dans une vraie fenêtre et permet de tester un modèle LLM sur plusieurs usages :

- générer du texte à partir d'un prompt ;
- réécrire un texte avec un style donné ;
- compléter des idées ;
- répondre à des questions ;
- répondre à des questions fréquentes de support client Expertisys ;
- donner des bonnes pratiques simples de cybersécurité.

## Modèle utilisé

Le modèle principal est :

```text
google/flan-t5-small
```

## Justification du modèle

`google/flan-t5-small` est adapté pour une maquette pédagogique car il est relativement léger, facile à charger avec Hugging Face Transformers et capable de répondre à des consignes simples. Il permet de tester les mécanismes principaux d'un assistant conversationnel sans mettre en place une infrastructure complexe.

La première exécution peut être plus longue car le modèle est téléchargé depuis Hugging Face.

## Structure du projet

```text
expertisys_agent/
│
├── main.py
├── requirements.txt
├── README.md
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

## Installation

Depuis le dossier `expertisys_agent`, installez les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement

Lancez l'application locale avec :

```bash
python main.py
```

Une fenêtre Tkinter intitulée **Assistant IA Expertisys** s'ouvre alors. L'utilisateur peut choisir le type de tâche, saisir un message, envoyer la demande et consulter la réponse dans l'historique de conversation.

## Fonctionnement

L'application suit les étapes suivantes :

1. récupération du texte utilisateur ;
2. recherche d'un contexte utile dans `data/expertisys_faq.json` ;
3. construction d'un prompt adapté à la tâche choisie ;
4. génération de la réponse avec `google/flan-t5-small` ;
5. nettoyage de la réponse ;
6. affichage dans l'interface Tkinter.

La génération est exécutée dans un thread séparé afin de garder l'interface réactive pendant que le modèle produit la réponse.

## Limites du prototype

Cette maquette n'est pas un assistant de production :

- la base de connaissances est une FAQ locale simplifiée ;
- la recherche repose sur des mots-clés, pas sur un vrai moteur RAG vectoriel ;
- le modèle peut produire des réponses incomplètes ou imprécises ;
- aucune authentification utilisateur n'est mise en place ;
- l'application ne doit pas traiter de données sensibles ;
- les conseils cybersécurité restent généraux et ne remplacent pas un expert.

## Conclusion

Ce projet fournit une base complète, simple et lisible pour présenter une maquette d'assistant conversationnel LLM pour Expertisys. Il peut être enrichi ensuite avec une meilleure recherche documentaire, un modèle plus puissant, une gestion d'utilisateurs et une intégration avec les outils internes de support.
