import threading
import tkinter as tk
from tkinter import ttk, messagebox

from src.knowledge_base import KnowledgeBase
from src.model import ExpertisysLLM
from src.prompts import build_prompt
from src.utils import (
    clean_response,
    get_example_prompts,
    get_task_from_label,
    get_task_label,
)


class ExpertisysApp:
    """Interface locale de démonstration pour l'assistant IA Expertisys."""

    def __init__(self, root):
        self.root = root
        self.root.title("Assistant IA Expertisys")
        self.root.geometry("1000x700")
        self.root.minsize(900, 620)

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

        self.is_generating = False

        # Chargement de la base de connaissances et du modèle au démarrage.
        self.knowledge_base = KnowledgeBase()
        self.llm = ExpertisysLLM()

        self._configure_style()
        self._build_interface()
        self._add_assistant_message(
            "Bonjour, je suis l'assistant IA Expertisys. "
            "Vous pouvez poser une question, demander une reformulation, "
            "générer un texte ou obtenir un conseil simple en cybersécurité."
        )

    def _configure_style(self):
        """Configure un style ttk sobre pour la maquette."""
        self.root.configure(bg=self.colors["background"])
        style = ttk.Style()
        style.theme_use("clam")

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
        chat_frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        chat_frame.rowconfigure(1, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        options = ttk.Frame(chat_frame, style="Panel.TFrame")
        options.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        options.columnconfigure(1, weight=1)
        options.columnconfigure(3, weight=1)

        ttk.Label(options, text="Tâche", style="Panel.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8)
        )

        self.task_labels = [
            get_task_label("question_answering"),
            get_task_label("generation"),
            get_task_label("rewriting"),
            get_task_label("completion"),
            get_task_label("cybersecurity"),
            get_task_label("support"),
        ]
        self.task_var = tk.StringVar(value=get_task_label("question_answering"))
        self.task_combo = ttk.Combobox(
            options,
            textvariable=self.task_var,
            values=self.task_labels,
            state="readonly",
            width=28,
        )
        self.task_combo.grid(row=0, column=1, sticky="ew", padx=(0, 14))
        self.task_combo.bind("<<ComboboxSelected>>", self._on_task_change)

        ttk.Label(options, text="Style", style="Panel.TLabel").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8)
        )

        self.style_var = tk.StringVar(value="professionnel")
        self.style_combo = ttk.Combobox(
            options,
            textvariable=self.style_var,
            values=["professionnel", "simple", "synthétique", "formel", "amical"],
            state="disabled",
            width=18,
        )
        self.style_combo.grid(row=0, column=3, sticky="ew")

        # Zone de chat avec historique des messages.
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
        side_panel = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        side_panel.grid(row=0, column=1, sticky="nsew")
        side_panel.columnconfigure(0, weight=1)

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

        examples_frame = ttk.Frame(side_panel, style="Panel.TFrame")
        examples_frame.grid(row=3, column=0, sticky="ew")
        examples_frame.columnconfigure(0, weight=1)

        for index, example in enumerate(get_example_prompts()):
            button = ttk.Button(
                examples_frame,
                text=example,
                command=lambda value=example: self.insert_example(value),
            )
            button.grid(row=index, column=0, sticky="ew", pady=3)

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

    def _on_task_change(self, _event=None):
        task_type = get_task_from_label(self.task_var.get())
        if task_type == "rewriting":
            self.style_combo.configure(state="readonly")
        else:
            self.style_combo.configure(state="disabled")

    def _update_scroll_region(self, _event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    def _resize_messages_frame(self, event):
        self.chat_canvas.itemconfig(self.messages_window, width=event.width)

    # Gestion de l'historique de conversation.
    def _add_message(self, sender, text, background, anchor):
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
        self._add_message("Vous", text, self.colors["user"], tk.E)

    def _add_assistant_message(self, text):
        self._add_message("Assistant Expertisys", text, self.colors["assistant"], tk.W)

    def _add_status_message(self, text):
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
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            self.status_label.destroy()

    def insert_example(self, example):
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        self.input_text.focus_set()

    def clear_conversation(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self._add_assistant_message("Conversation effacée. Comment puis-je vous aider ?")

    def send_message(self):
        if self.is_generating:
            return

        user_text = self.input_text.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showinfo("Message vide", "Veuillez saisir un message.")
            return

        if not self.llm.is_ready:
            self._add_assistant_message(self.llm.load_error)
            return

        self.input_text.delete("1.0", tk.END)
        self._add_user_message(user_text)
        self._set_generation_state(True)

        # Le thread permet de garder l'interface active pendant la génération.
        thread = threading.Thread(
            target=self._generate_response_worker,
            args=(user_text, self.task_var.get(), self.style_var.get()),
            daemon=True,
        )
        thread.start()

    def _set_generation_state(self, generating):
        self.is_generating = generating
        if generating:
            self.send_button.configure(state="disabled")
            self._add_status_message("Génération de la réponse en cours...")
        else:
            self.send_button.configure(state="normal")
            self._remove_status_message()

    # Génération de réponse à partir du modèle et de la base Expertisys.
    def _generate_response_worker(self, user_text, task_label, style):
        try:
            task_type = get_task_from_label(task_label)
            context = self.knowledge_base.search(user_text)
            prompt = build_prompt(
                task_type=task_type,
                user_text=user_text,
                style=style,
                context=context,
            )
            response = self.llm.generate(prompt)
            response = clean_response(response)
        except Exception as exc:
            response = (
                "Une erreur est survenue pendant la génération. "
                f"Détail technique : {exc}"
            )

        self.root.after(0, self._display_generated_response, response)

    def _display_generated_response(self, response):
        self._set_generation_state(False)
        self._add_assistant_message(response)


def main():
    root = tk.Tk()
    ExpertisysApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
