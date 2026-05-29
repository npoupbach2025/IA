import unittest

from src.prompts import FRENCH_ONLY_INSTRUCTION, PROMPT_TEMPLATES, build_prompt


class PromptTests(unittest.TestCase):
    """Tests de construction des prompts envoyés au modèle."""

    def test_all_expected_task_types_have_templates(self):
        expected_tasks = {
            "question_answering",
            "generation",
            "rewriting",
            "completion",
            "cybersecurity",
            "support",
        }

        self.assertTrue(expected_tasks.issubset(PROMPT_TEMPLATES))
        for task_type in expected_tasks:
            self.assertGreaterEqual(len(PROMPT_TEMPLATES[task_type]), 1)

    def test_build_prompt_includes_french_rule(self):
        prompt = build_prompt("support", "Je n'arrive pas à me connecter")

        self.assertTrue(prompt.startswith(FRENCH_ONLY_INSTRUCTION))
        self.assertIn("français", prompt)
        self.assertIn("Je n'arrive pas à me connecter", prompt)

    def test_build_prompt_adds_context_when_available(self):
        prompt = build_prompt(
            "question_answering",
            "Comment contacter le support ?",
            context="Réponse Expertisys : utilisez le portail client.",
        )

        self.assertIn("Contexte utile provenant de la base Expertisys", prompt)
        self.assertIn("utilisez le portail client", prompt)

    def test_rewriting_prompt_uses_selected_style(self):
        prompt = build_prompt(
            "rewriting",
            "j'ai un problème avec mon accès",
            style="formel",
        )

        self.assertIn("formel", prompt)
        self.assertIn("j'ai un problème avec mon accès", prompt)

    def test_unknown_task_falls_back_to_question_answering(self):
        prompt = build_prompt("unknown", "Que fait Expertisys ?")

        self.assertIn("Que fait Expertisys ?", prompt)
        self.assertIn("Expertisys", prompt)


if __name__ == "__main__":
    unittest.main()
