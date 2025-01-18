from typing import Dict, List
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ResumeScorer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
    def _get_embeddings(self, text: str) -> np.ndarray:
        """Get embeddings for text using transformer model."""
        inputs = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()
        
    def calculate_match_score(
        self, 
        resume_data: Dict, 
        job_data: Dict
    ) -> Dict[str, float]:
        """Calculate how well the resume matches the job requirements."""
        scores = {
            'skills_match': self._score_skills_match(
                resume_data['skills'], 
                job_data['skills']
            ),
            'experience_match': self._score_experience_match(
                resume_data['experiences'], 
                job_data['requirements']
            ),
            'education_match': self._score_education_match(
                resume_data['education'], 
                job_data['requirements']
            )
        }
        
        scores['overall_match'] = sum(scores.values()) / len(scores)
        return scores

    def _score_skills_match(self, resume_skills: Dict[str, List[str]], job_skills: Dict[str, List[str]]) -> float:
        """Calculate skills match score using semantic similarity."""
        # Implementation

    def _score_experience_match(self, experiences: List[Dict], requirements: List[str]) -> float:
        """Calculate experience match score using semantic similarity."""
        if not requirements:
            return 1.0
        
        experience_text = " ".join([
            " ".join(exp.get('highlights', [])) 
            for exp in experiences
        ])
        
        # Calculate semantic similarity using transformers
        exp_emb = self._get_embeddings(experience_text)
        req_emb = self._get_embeddings(" ".join(requirements))
        
        similarity = cosine_similarity(exp_emb, req_emb)[0][0]
        return float(similarity)

    def _score_education_match(self, education: List[Dict], requirements: List[str]) -> float:
        """Calculate education match score using semantic similarity."""
        if not requirements or not education:
            return 0.0
        
        education_text = " ".join([
            f"{edu.get('school', '')} {' '.join(deg.get('names', []))}"
            for edu in education
            for deg in edu.get('degrees', [])
        ])
        
        # Calculate semantic similarity using transformers
        edu_emb = self._get_embeddings(education_text)
        req_emb = self._get_embeddings(" ".join(requirements))
        
        similarity = cosine_similarity(edu_emb, req_emb)[0][0]
        return float(similarity) 