import unittest
from unittest.mock import MagicMock, patch

from src.model import ExpertisysLLM, FALLBACK_RESPONSE


class ModelTests(unittest.TestCase):
    """Tests du wrapper de modèle sans télécharger google/flan-t5-small."""

    @patch("src.model.AutoModelForSeq2SeqLM")
    @patch("src.model.AutoTokenizer")
    def test_model_is_loaded_once_and_set_to_eval(self, tokenizer_cls, model_cls):
        tokenizer = MagicMock()
        model = MagicMock()
        tokenizer_cls.from_pretrained.return_value = tokenizer
        model_cls.from_pretrained.return_value = model

        llm = ExpertisysLLM()

        self.assertTrue(llm.is_ready)
        self.assertEqual(llm.model_name, "google/flan-t5-small")
        tokenizer_cls.from_pretrained.assert_called_once_with("google/flan-t5-small")
        model_cls.from_pretrained.assert_called_once_with("google/flan-t5-small")
        model.eval.assert_called_once()

    @patch("src.model.AutoModelForSeq2SeqLM")
    @patch("src.model.AutoTokenizer")
    def test_generate_returns_fallback_when_response_is_empty(self, tokenizer_cls, model_cls):
        tokenizer = MagicMock()
        tokenizer.return_value = {"input_ids": MagicMock()}
        tokenizer.decode.return_value = ""

        model = MagicMock()
        model.generate.return_value = ["empty-output"]

        tokenizer_cls.from_pretrained.return_value = tokenizer
        model_cls.from_pretrained.return_value = model

        llm = ExpertisysLLM()
        response = llm.generate("prompt test")

        self.assertEqual(response, FALLBACK_RESPONSE)

    @patch("src.model.AutoModelForSeq2SeqLM")
    @patch("src.model.AutoTokenizer")
    def test_load_error_is_handled_cleanly(self, tokenizer_cls, _model_cls):
        tokenizer_cls.from_pretrained.side_effect = RuntimeError("download failed")

        llm = ExpertisysLLM()

        self.assertFalse(llm.is_ready)
        self.assertIn("n'a pas pu être chargé", llm.load_error)


if __name__ == "__main__":
    unittest.main()
