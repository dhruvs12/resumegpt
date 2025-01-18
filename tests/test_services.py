import unittest
from unittest.mock import patch, MagicMock
from ..services.resume_improver import ResumeImprover
from ..services.resume_scorer import ResumeScorer
import numpy as np


class TestResumeScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ResumeScorer()
        
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModel.from_pretrained')
    def test_get_embeddings(self, mock_model, mock_tokenizer):
        # Mock the transformer model outputs
        mock_output = MagicMock()
        mock_output.last_hidden_state = np.random.rand(1, 10, 768)  # Example dimensions
        mock_model.return_value.return_value = mock_output
        
        text = "Test text"
        embeddings = self.scorer._get_embeddings(text)
        
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape[1], 768)  # Standard BERT embedding size

    def test_score_skills_match(self):
        resume_skills = [{"skills": ["Python", "Machine Learning"]}]
        job_skills = {
            "technical_skills": ["Python", "Deep Learning"],
            "non_technical_skills": ["Communication"]
        }
        
        score = self.scorer._score_skills_match(resume_skills, job_skills)
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 1)
