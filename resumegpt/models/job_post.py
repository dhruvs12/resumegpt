from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from ..prompts.prompts import Prompts
from .. import config
from langchain_google_genai import ChatGoogleGenerativeAI
from bs4 import BeautifulSoup
import re
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

class JobSkills(BaseModel):
    """Skills required for the job."""
    technical_skills: List[str] = Field(default_factory=list)
    non_technical_skills: List[str] = Field(default_factory=list)
    ats_keywords: List[str] = Field(default_factory=list)

class JobRequirements(BaseModel):
    """Requirements for the job."""
    qualifications: List[str] = Field(default_factory=list)
    duties: List[str] = Field(default_factory=list)

class JobDescription(BaseModel):
    """Complete job posting description."""
    company: Optional[str] = None
    job_title: Optional[str] = None
    skills: JobSkills = Field(default_factory=JobSkills)
    requirements: JobRequirements = Field(default_factory=JobRequirements)

class JobPost:
    def __init__(self, posting: str):
        self.raw_content = posting
        self.cleaned_content = None
        self.parsed_job = None
        self.extractor_llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.2  # Lower temperature for more consistent parsing
        )

    def clean_html_content(self):
        """Clean and normalize HTML content."""
        soup = BeautifulSoup(self.raw_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and normalize spaces
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        self.cleaned_content = text
        return text

    def extract_section(self, text: str, section_name: str) -> List[str]:
        """Extract specific sections from job posting."""
        prompt = f"""Extract the {section_name} from this job posting. Return as a list of strings.
        Job Posting: {text}
        
        Rules:
        - Each item should be a complete, meaningful phrase
        - Remove duplicates
        - Maximum 10 items
        - Return only the list, no explanations
        """
        
        response = self.extractor_llm.invoke(prompt)
        # Process response to extract list items
        items = re.findall(r'[-•*]\s*(.+)', response.content)
        if not items:
            # Try alternative parsing if bullet points aren't found
            items = [line.strip() for line in response.content.split('\n') if line.strip()]
        return items[:10]  # Limit to 10 items

    def parse_job_post(self, verbose=False) -> dict:
        """Parse the job posting into structured data."""
        try:
            # Clean HTML content first
            cleaned_text = self.clean_html_content()
            
            # Extract each section separately
            technical_skills = self.extract_section(cleaned_text, "technical skills and tools required")
            non_technical_skills = self.extract_section(cleaned_text, "soft skills and competencies required")
            qualifications = self.extract_section(cleaned_text, "qualifications and requirements")
            duties = self.extract_section(cleaned_text, "main responsibilities and duties")
            ats_keywords = self.extract_section(cleaned_text, "important keywords and industry terms")

            # Create structured output
            self.parsed_job = JobDescription(
                company=self.extract_company_name(cleaned_text),
                job_title=self.extract_job_title(cleaned_text),
                skills=JobSkills(
                    technical_skills=technical_skills,
                    non_technical_skills=non_technical_skills,
                    ats_keywords=ats_keywords
                ),
                requirements=JobRequirements(
                    qualifications=qualifications,
                    duties=duties
                )
            )

            return self.parsed_job.dict()
            
        except Exception as e:
            config.logger.error(f"Failed to parse job post: {str(e)}")
            raise

    def extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from job posting."""
        prompt = "What is the company name in this job posting? Return only the name."
        response = self.extractor_llm.invoke(prompt + "\n" + text[:1000])
        return response.content.strip()

    def extract_job_title(self, text: str) -> Optional[str]:
        """Extract job title from job posting."""
        prompt = "What is the job title in this job posting? Return only the title."
        response = self.extractor_llm.invoke(prompt + "\n" + text[:1000])
        return response.content.strip()

class JobAnalyzer:
    def __init__(self):
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
    def analyze_job_posting(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of job posting."""
        return {
            'requirements': self.extract_requirements(text),
            'skills': self.extract_skills(text),
            'company_culture': self.analyze_company_culture(text),
            'keywords': self.extract_ats_keywords(text),
            'seniority_level': self.determine_seniority(text)
        }
        
    def analyze_company_culture(self, text: str) -> Dict[str, float]:
        """Analyze company culture and values using sentiment analysis."""
        culture_indicators = {
            'innovation': ['innovative', 'cutting-edge', 'pioneering'],
            'collaboration': ['team', 'collaborative', 'cross-functional'],
            'growth': ['learning', 'development', 'mentorship']
        }
        
        scores = {}
        for value, keywords in culture_indicators.items():
            # Get sentiment scores for sentences containing culture keywords
            relevant_sentences = [sent for sent in text.split('.') 
                               if any(keyword in sent.lower() for keyword in keywords)]
            if relevant_sentences:
                sentiments = self.sentiment_pipeline(relevant_sentences)
                scores[value] = sum(s['score'] for s in sentiments) / len(sentiments)
            else:
                scores[value] = 0.0
                
        return scores

    def extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements using NLP."""
        requirements = []
        for sent in text.split('.') if '.' in text else []:
            if any(keyword in sent.lower() for keyword in ['require', 'must', 'should', 'need']):
                requirements.append(sent.strip())
        return requirements

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from job posting."""
        skills = {
            'technical': [],
            'soft': []
        }
        
        # Define skill indicators
        technical_indicators = ['programming', 'software', 'technical', 'technology']
        soft_indicators = ['communication', 'interpersonal', 'leadership']
        
        for sent in text.split('.') if '.' in text else []:
            sent_lower = sent.lower()
            
            # Classify skills based on context
            if any(ind in sent_lower for ind in technical_indicators):
                skills['technical'].extend([
                    ent.strip() for ent, label in self.ner_pipeline(sent) 
                    if label == 'PRODUCT' or label == 'ORG' or label == 'TECH'
                ])
            elif any(ind in sent_lower for ind in soft_indicators):
                skills['soft'].extend([
                    ent.strip() for ent, label in self.ner_pipeline(sent) 
                    if label == 'SKILL'
                ])
            
        return skills

    def determine_seniority(self, text: str) -> str:
        """Determine job seniority level."""
        seniority_indicators = {
            'entry': ['entry', 'junior', 'graduate'],
            'mid': ['mid', 'intermediate', 'experienced'],
            'senior': ['senior', 'lead', 'principal']
        }
        
        text_lower = text.lower()
        for level, indicators in seniority_indicators.items():
            if any(ind in text_lower for ind in indicators):
                return level
            
        return 'not_specified'
