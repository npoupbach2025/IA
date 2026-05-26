"""
Point d'entrée de l'application locale Expertisys.

Ce fichier contient toute l'interface graphique Tkinter. Le rôle de main.py est
de faire le lien entre l'utilisateur, la base FAQ locale et le modèle LLM.
Les traitements métier sont volontairement placés dans le dossier src/ pour
garder une structure de projet claire.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from src.knowledge_base import KnowledgeBase
from src.model import ExpertisysLLM
from src.prompts import build_prompt
from src.utils import (
    build_french_fallback_response,
    build_email_response,
    build_password_response,
    clean_response,
    detect_task_type,
    get_example_prompts,
    get_task_label,
    is_email_request,
    is_password_request,
    response_needs_french_fallback,
)


class ExpertisysApp:
    """
    Fenêtre principale de la maquette.

    La classe regroupe :
    - la création des composants Tkinter ;
    - l'affichage de l'historique de conversation ;
    - l'appel à la base de connaissances ;
    - l'appel au modèle LLM dans un thread séparé.
    """

    def __init__(self, root):
        # La fenêtre root est créée dans la fonction main(), puis transmise ici
        # pour que toute l'interface soit organisée dans cette classe.
        self.root = root
        self.root.title("Assistant IA Expertisys")
        self.root.geometry("1000x700")
        self.root.minsize(900, 620)

        # Les couleurs sont centralisées pour faciliter la modification du
        # style visuel sans devoir chercher dans tout le fichier.
        self.colors = {
            "header": "#123456",
            "background": "#f4f6f8",
            "panel": "#ffffff",
            "user": "#dceeff",
            "assistant": "#eef2f5",
            "text": "#1f2933",
            "muted": "#5f6b7a",
            "accent": "#1d72b8",
        }

        # Ce booléen évite d'envoyer plusieurs messages en même temps pendant
        # que le modèle est déjà en train de générer une réponse.
        self.is_generating = False

        # Chargement de la base de connaissances et du modèle au démarrage.
        # Le modèle peut prendre du temps au premier lancement car Hugging Face
        # doit parfois télécharger les fichiers.
        self.knowledge_base = KnowledgeBase()
        self.llm = ExpertisysLLM()

        # Une fois les dépendances prêtes, on construit l'écran et on affiche
        # un premier message pour guider l'utilisateur.
        self._configure_style()
        self._build_interface()
        self._add_assistant_message(
            "Bonjour, je suis l'assistant IA Expertisys. "
            "Vous pouvez poser une question, demander une reformulation, "
            "générer un texte ou obtenir un conseil simple en cybersécurité."
        )

    def _configure_style(self):
        """
        Configure le thème graphique ttk.

        ttk permet d'avoir des composants plus propres que les widgets Tkinter
        classiques. Le thème reste volontairement sobre pour une présentation
        professionnelle devant un jury.
        """
        self.root.configure(bg=self.colors["background"])
        style = ttk.Style()
        style.theme_use("clam")

        # Styles généraux des conteneurs.
        style.configure(
            "TFrame",
            background=self.colors["background"],
        )
        style.configure(
            "Panel.TFrame",
            background=self.colors["panel"],
        )
        style.configure(
            "Header.TFrame",
            background=self.colors["header"],
        )

        # Styles du titre et du sous-titre dans l'en-tête.
        style.configure(
            "Title.TLabel",
            background=self.colors["header"],
            foreground="white",
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["header"],
            foreground="#d7e2ee",
            font=("Segoe UI", 10),
        )

        # Styles des textes, boutons et menus déroulants.
        style.configure(
            "TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Panel.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Muted.Panel.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Accent.TButton",
            background=self.colors["accent"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(10, 6),
        )
        style.configure(
            "TCombobox",
            padding=(6, 4),
        )

    # Interface Tkinter principale.
    def _build_interface(self):
        """
        Construit la structure principale de la fenêtre.

        L'écran est divisé en trois zones :
        - un en-tête en haut ;
        - la conversation à gauche ;
        - un panneau d'information et d'exemples à droite.
        """
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(24, 18))
        header.pack(fill=tk.X)

        ttk.Label(header, text="Assistant IA Expertisys", style="Title.TLabel").pack(
            anchor=tk.W
        )
        ttk.Label(
            header,
            text="Maquette d'agent conversationnel basé sur un LLM",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        body = ttk.Frame(self.root, padding=16)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_chat_area(body)
        self._build_side_panel(body)

    def _build_chat_area(self, parent):
        """Crée la zone centrale : choix de tâche, historique et saisie."""
        chat_frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        chat_frame.rowconfigure(1, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        # Ligne supérieure : la tâche est détectée automatiquement à partir du
        # message utilisateur. On garde seulement le style comme option utile
        # pour les demandes de reformulation.
        options = ttk.Frame(chat_frame, style="Panel.TFrame")
        options.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        options.columnconfigure(1, weight=1)
        options.columnconfigure(3, weight=1)

        ttk.Label(options, text="Tâche", style="Panel.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8)
        )

        self.detected_task_var = tk.StringVar(value="Détection automatique")
        ttk.Label(
            options,
            textvariable=self.detected_task_var,
            style="Panel.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=1, sticky=tk.W, padx=(0, 14))

        ttk.Label(options, text="Style", style="Panel.TLabel").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8)
        )

        self.style_var = tk.StringVar(value="professionnel")
        self.style_combo = ttk.Combobox(
            options,
            textvariable=self.style_var,
            values=["professionnel", "simple", "synthétique", "formel", "amical"],
            state="readonly",
            width=18,
        )
        self.style_combo.grid(row=0, column=3, sticky="ew")

        # Zone de chat avec historique des messages.
        # Un Canvas est utilisé car il permet d'ajouter un contenu défilable
        # composé de bulles de conversation.
        chat_container = ttk.Frame(chat_frame, style="Panel.TFrame")
        chat_container.grid(row=1, column=0, sticky="nsew")
        chat_container.rowconfigure(0, weight=1)
        chat_container.columnconfigure(0, weight=1)

        self.chat_canvas = tk.Canvas(
            chat_container,
            bg=self.colors["panel"],
            highlightthickness=0,
        )
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            chat_container, orient=tk.VERTICAL, command=self.chat_canvas.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        self.messages_frame = tk.Frame(self.chat_canvas, bg=self.colors["panel"])
        self.messages_window = self.chat_canvas.create_window(
            (0, 0), window=self.messages_frame, anchor="nw"
        )

        self.messages_frame.bind("<Configure>", self._update_scroll_region)
        self.chat_canvas.bind("<Configure>", self._resize_messages_frame)

        # Zone du bas : champ de saisie et boutons d'action.
        input_frame = ttk.Frame(chat_frame, style="Panel.TFrame")
        input_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        input_frame.columnconfigure(0, weight=1)

        self.input_text = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg=self.colors["text"],
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=8,
        )
        self.input_text.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_text.bind("<Control-Return>", lambda event: self.send_message())

        buttons = ttk.Frame(input_frame, style="Panel.TFrame")
        buttons.grid(row=0, column=1, sticky="ns")

        self.send_button = ttk.Button(
            buttons,
            text="Envoyer",
            style="Accent.TButton",
            command=self.send_message,
        )
        self.send_button.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(
            buttons,
            text="Effacer la conversation",
            command=self.clear_conversation,
        ).pack(fill=tk.X)

    def _build_side_panel(self, parent):
        """
        Crée la colonne de droite.

        Elle donne des informations rapides sur le prototype et propose des
        exemples de prompts pour tester l'application sans devoir inventer une
        question à chaque fois.
        """
        side_panel = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        side_panel.grid(row=0, column=1, sticky="nsew")
        side_panel.columnconfigure(0, weight=1)
        side_panel.rowconfigure(3, weight=1)

        ttk.Label(
            side_panel,
            text="Prototype Expertisys",
            style="Panel.TLabel",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            side_panel,
            text="Modèle utilisé : google/flan-t5-small",
            style="Muted.Panel.TLabel",
            wraplength=240,
        ).grid(row=1, column=0, sticky=tk.W, pady=(8, 18))

        ttk.Label(
            side_panel,
            text="Exemples de prompts",
            style="Panel.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        # Comme il y a maintenant beaucoup d'exemples, on les place dans une
        # petite zone défilable. L'interface reste ainsi propre même sur un écran
        # de taille moyenne.
        examples_container = ttk.Frame(side_panel, style="Panel.TFrame")
        examples_container.grid(row=3, column=0, sticky="nsew")
        examples_container.rowconfigure(0, weight=1)
        examples_container.columnconfigure(0, weight=1)

        examples_canvas = tk.Canvas(
            examples_container,
            bg=self.colors["panel"],
            highlightthickness=0,
            height=280,
        )
        examples_canvas.grid(row=0, column=0, sticky="nsew")

        examples_scrollbar = ttk.Scrollbar(
            examples_container,
            orient=tk.VERTICAL,
            command=examples_canvas.yview,
        )
        examples_scrollbar.grid(row=0, column=1, sticky="ns")
        examples_canvas.configure(yscrollcommand=examples_scrollbar.set)

        examples_frame = tk.Frame(examples_canvas, bg=self.colors["panel"])
        examples_window = examples_canvas.create_window(
            (0, 0),
            window=examples_frame,
            anchor="nw",
        )

        examples_frame.bind(
            "<Configure>",
            lambda _event: examples_canvas.configure(
                scrollregion=examples_canvas.bbox("all")
            ),
        )
        examples_canvas.bind(
            "<Configure>",
            lambda event: examples_canvas.itemconfig(
                examples_window,
                width=event.width,
            ),
        )

        for index, example in enumerate(get_example_prompts()):
            # Le lambda avec value=example mémorise la valeur actuelle de la
            # boucle. Sans cela, tous les boutons utiliseraient le dernier exemple.
            button = tk.Button(
                examples_frame,
                text=example,
                command=lambda value=example: self.insert_example(value),
                bg="#f7f9fb",
                fg=self.colors["text"],
                activebackground="#e7eef6",
                activeforeground=self.colors["text"],
                relief=tk.SOLID,
                borderwidth=1,
                padx=8,
                pady=6,
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=225,
                font=("Segoe UI", 9),
            )
            button.pack(fill=tk.X, pady=3)

        ttk.Separator(side_panel).grid(row=4, column=0, sticky="ew", pady=18)

        ttk.Label(
            side_panel,
            text="Limites du prototype",
            style="Panel.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=5, column=0, sticky=tk.W)

        limits = (
            "Cette maquette fonctionne localement et utilise une base FAQ simplifiée. "
            "Elle ne remplace pas un support officiel, ne vérifie pas l'identité des "
            "utilisateurs et ne doit pas être utilisée pour traiter des données sensibles."
        )
        ttk.Label(
            side_panel,
            text=limits,
            style="Muted.Panel.TLabel",
            wraplength=250,
            justify=tk.LEFT,
        ).grid(row=6, column=0, sticky=tk.W, pady=(8, 0))

    def _update_detected_task(self, task_type):
        """Affiche dans l'interface la tâche détectée automatiquement."""
        label = get_task_label(task_type)
        self.detected_task_var.set(f"Détectée : {label}")

    def _update_scroll_region(self, _event=None):
        """Met à jour la zone défilable quand un nouveau message est ajouté."""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    def _resize_messages_frame(self, event):
        """Garde les bulles de conversation adaptées à la largeur disponible."""
        self.chat_canvas.itemconfig(self.messages_window, width=event.width)

    # Gestion de l'historique de conversation.
    def _add_message(self, sender, text, background, anchor):
        """
        Ajoute une bulle dans l'historique.

        Le même code sert pour l'utilisateur et l'assistant. La couleur et
        l'alignement changent selon l'expéditeur.
        """
        wrapper = tk.Frame(self.messages_frame, bg=self.colors["panel"])
        wrapper.pack(fill=tk.X, pady=6, padx=4)

        bubble = tk.Frame(wrapper, bg=background, padx=12, pady=8)
        bubble.pack(anchor=anchor, padx=8)

        title = tk.Label(
            bubble,
            text=sender,
            bg=background,
            fg=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        )
        title.pack(anchor=tk.W)

        message = tk.Label(
            bubble,
            text=text,
            bg=background,
            fg=self.colors["text"],
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            wraplength=560,
        )
        message.pack(anchor=tk.W, pady=(3, 0))

        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _add_user_message(self, text):
        """Affiche un message envoyé par l'utilisateur, aligné à droite."""
        self._add_message("Vous", text, self.colors["user"], tk.E)

    def _add_assistant_message(self, text):
        """Affiche une réponse de l'assistant, alignée à gauche."""
        self._add_message("Assistant Expertisys", text, self.colors["assistant"], tk.W)

    def _add_status_message(self, text):
        """Affiche un petit message temporaire pendant la génération."""
        self.status_label = tk.Label(
            self.messages_frame,
            text=text,
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9, "italic"),
        )
        self.status_label.pack(anchor=tk.W, pady=4, padx=14)
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _remove_status_message(self):
        """Supprime le message temporaire une fois la génération terminée."""
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            self.status_label.destroy()

    def insert_example(self, example):
        """Insère un exemple de prompt dans la zone de saisie."""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        self.input_text.focus_set()

    def clear_conversation(self):
        """Efface tout l'historique affiché dans la zone de chat."""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self._add_assistant_message("Conversation effacée. Comment puis-je vous aider ?")

    def send_message(self):
        """
        Récupère le message utilisateur et lance la génération.

        Cette méthode reste courte : elle vérifie les cas simples, affiche le
        message utilisateur, puis délègue le travail long au thread.
        """
        if self.is_generating:
            return

        # Tkinter ajoute souvent un retour à la ligne final dans un widget Text,
        # donc strip() permet de récupérer uniquement le vrai message.
        user_text = self.input_text.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showinfo("Message vide", "Veuillez saisir un message.")
            return

        if not self.llm.is_ready and not (
            is_email_request(user_text) or is_password_request(user_text)
        ):
            self._add_assistant_message(self.llm.load_error)
            return

        # Le message est affiché immédiatement pour que l'interface réagisse
        # dès le clic sur Envoyer.
        self.input_text.delete("1.0", tk.END)
        self._add_user_message(user_text)
        self._set_generation_state(True)

        # Le thread permet de garder l'interface active pendant la génération.
        # Sans thread, la fenêtre se figerait pendant que PyTorch calcule la réponse.
        thread = threading.Thread(
            target=self._generate_response_worker,
            args=(user_text, self.style_var.get()),
            daemon=True,
        )
        thread.start()

    def _set_generation_state(self, generating):
        """Change l'état visuel selon que le modèle travaille ou non."""
        self.is_generating = generating
        if generating:
            self.send_button.configure(state="disabled")
            self._add_status_message("Génération de la réponse en cours...")
        else:
            self.send_button.configure(state="normal")
            self._remove_status_message()

    # Génération de réponse à partir du modèle et de la base Expertisys.
    def _generate_response_worker(self, user_text, style):
        """
        Travail exécuté dans le thread secondaire.

        Attention : Tkinter n'est pas entièrement thread-safe. C'est pour cela
        que cette méthode ne modifie pas directement l'interface. Elle prépare
        la réponse, puis utilise root.after() pour revenir dans le thread Tkinter.
        """
        try:
            # La tâche est déterminée automatiquement à partir du texte saisi.
            # L'utilisateur n'a donc plus besoin de choisir un mode dans un menu.
            task_type = detect_task_type(user_text)
            self.root.after(0, self._update_detected_task, task_type)

            # Pour les demandes simples de rédaction de mail, on utilise une
            # réponse structurée contrôlée. Cela évite que le petit modèle
            # recopie le prompt au lieu de rédiger le message attendu.
            if is_email_request(user_text):
                response = build_email_response(user_text)
                response = clean_response(response)
                self.root.after(0, self._display_generated_response, response)
                return

            # Même logique pour le changement de mot de passe : c'est une FAQ
            # critique, donc on préfère une réponse française sûre et stable.
            if is_password_request(user_text):
                response = build_password_response()
                response = clean_response(response)
                self.root.after(0, self._display_generated_response, response)
                return

            # Si la FAQ contient une information proche, elle est ajoutée au
            # prompt comme contexte utile.
            context = self.knowledge_base.search(user_text)
            prompt = build_prompt(
                task_type=task_type,
                user_text=user_text,
                style=style,
                context=context,
            )

            # Le prompt interne n'est jamais affiché à l'utilisateur. Il sert
            # uniquement à guider le modèle.
            response = self.llm.generate(prompt)
            response = clean_response(response)

            # Dernier garde-fou : si le modèle répond en anglais ou recopie des
            # morceaux du prompt, on remplace par une réponse française contrôlée.
            if response_needs_french_fallback(response):
                response = build_french_fallback_response(user_text, context)
        except Exception as exc:
            response = (
                "Une erreur est survenue pendant la génération. "
                f"Détail technique : {exc}"
            )

        self.root.after(0, self._display_generated_response, response)

    def _display_generated_response(self, response):
        """Réactive l'interface et affiche la réponse finale."""
        self._set_generation_state(False)
        self._add_assistant_message(response)


def main():
    """Crée la fenêtre Tkinter et lance la boucle événementielle."""
    root = tk.Tk()
    ExpertisysApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
