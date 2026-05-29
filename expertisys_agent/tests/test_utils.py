import unittest

from src.utils import (
    build_email_response,
    build_french_fallback_response,
    build_password_response,
    detect_task_type,
    get_task_label,
    is_email_request,
    is_password_request,
    response_needs_french_fallback,
)


class UtilsTests(unittest.TestCase):
    """Tests des fonctions utilitaires et du routage automatique."""

    def test_detect_task_type_for_common_requests(self):
        cases = {
            "Comment créer un mot de passe sécurisé ?": "cybersecurity",
            "Réécris ce message dans un style professionnel": "rewriting",
            "Message pour confirmer la prise en charge d'un ticket": "generation",
            "Pour améliorer la sécurité des postes utilisateurs, il faut...": "completion",
            "Je n'arrive pas à me connecter à mon compte": "support",
            "Quelle est la mission d'Expertisys ?": "question_answering",
        }

        for user_text, expected_task in cases.items():
            with self.subTest(user_text=user_text):
                self.assertEqual(detect_task_type(user_text), expected_task)

    def test_task_labels_are_french(self):
        self.assertEqual(get_task_label("support"), "Support client Expertisys")
        self.assertEqual(get_task_label("unknown"), "Répondre à une question")

    def test_email_request_detection_and_response(self):
        user_text = "écris un mail pour dire que mon compte est bloqué"

        self.assertTrue(is_email_request(user_text))
        response = build_email_response(user_text)

        self.assertIn("Objet :", response)
        self.assertIn("Bonjour", response)
        self.assertIn("compte est actuellement bloqué", response)
        self.assertIn("Cordialement", response)

    def test_password_request_detection_and_response(self):
        user_text = "peux-tu me dire comment changer mon mot de passe ?"

        self.assertTrue(is_password_request(user_text))
        response = build_password_response()

        self.assertIn("Mot de passe oublié", response)
        self.assertIn("support Expertisys", response)

    def test_english_response_is_detected(self):
        bad_response = "What should I do if I want to change my password?"
        good_response = "Vous pouvez réinitialiser votre mot de passe depuis la page de connexion."

        self.assertTrue(response_needs_french_fallback(bad_response))
        self.assertFalse(response_needs_french_fallback(good_response))

    def test_french_fallback_uses_context_answer(self):
        context = (
            "Question proche : Comment contacter le support ?\n"
            "Réponse Expertisys : Contactez le support depuis le portail client.\n"
            "Catégorie : support"
        )

        response = build_french_fallback_response("support", context)

        self.assertIn("Contactez le support depuis le portail client", response)


if __name__ == "__main__":
    unittest.main()
