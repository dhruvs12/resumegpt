from typing import Dict, Any, Union
import re
import yaml
from PyPDF2 import PdfReader
from docx import Document
import textract
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

class ResumeParser:
    def __init__(self):
        # Initialize transformers models
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume from various file formats into structured data."""
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext == 'yaml':
            return self.parse_yaml_resume(file_path)
        elif file_ext == 'pdf':
            return self.parse_pdf_resume(file_path)
        elif file_ext in ['doc', 'docx']:
            return self.parse_word_resume(file_path)
        elif file_ext == 'txt':
            return self.parse_text_resume(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from resume text using keyword matching and transformers."""
        sections = {
            'education': '',
            'experience': '',
            'skills': '',
            'projects': ''
        }
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        current_section = None
        
        for para in paragraphs:
            para_lower = para.lower().strip()
            # Check for section headers
            if any(section in para_lower for section in sections.keys()):
                current_section = next(s for s in sections.keys() 
                                    if s in para_lower)
            elif current_section:
                sections[current_section] += para + '\n'
                
        return sections

    def parse_pdf_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF resume into structured data."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            sections = self.extract_sections(text)
            return self._structure_resume_data(sections)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF resume: {str(e)}")

    def parse_word_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse Word document resume into structured data."""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            sections = self.extract_sections(text)
            return self._structure_resume_data(sections)
        except Exception as e:
            raise ValueError(f"Failed to parse Word resume: {str(e)}")

    def _structure_resume_data(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Convert extracted sections into structured resume data."""
        structured_data = {
            'basic': self._extract_basic_info(sections),
            'education': self._extract_education(sections['education']),
            'experiences': self._extract_experiences(sections['experience']),
            'projects': self._extract_projects(sections['projects']),
            'skills': self._extract_skills(sections['skills'])
        }
        return structured_data

    def _extract_basic_info(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract basic information using NER and regex."""
        info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'websites': []
        }
        
        # Use NER pipeline for name and location
        text = sections.get('basic', '')
        entities = self.ner_pipeline(text)
        
        for entity in entities:
            if entity['entity_group'] == 'PER':
                info['name'] = entity['word']
            elif entity['entity_group'] == 'LOC':
                info['location'] = entity['word']
        
        # Extract email and phone using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        if emails:
            info['email'] = emails[0]
        if phones:
            info['phone'] = phones[0]
            
        return info

    def extract_entities(self, text):
        """Extract named entities using transformers NER pipeline."""
        entities = self.ner_pipeline(text)
        return [(entity['word'], entity['entity_group']) for entity in entities] 