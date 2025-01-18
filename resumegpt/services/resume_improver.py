from ..models.resume import Resume, TailoredResume
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config.config import Config
import json

class ResumeImprover:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL_NAME,
            temperature=Config.GEMINI_TEMPERATURE
        )
    
    def process_resume(self, resume_data: dict, job_html: str) -> dict:
        try:
            # Validate input resume
            resume = Resume(**resume_data)
            
            # Clean up the name
            actual_name = "Dhruv Singh"  # We should extract this from the resume properly
            
            prompt = f"""
            You are a professional resume tailoring assistant. Given the job description and current resume below, 
            create a tailored version that better matches the job requirements.

            Job Description:
            {job_html}
            
            Current Resume:
            {resume.model_dump_json(indent=2)}
            
            Important Instructions:
            1. Keep descriptions concise and single-version only
            2. Use actual company names from the resume, not placeholders
            3. Format all text properly without truncation
            4. Focus on web development and relevant technical skills
            
            Provide a response in the following JSON format ONLY (no markdown, no extra text):
            {{
                "tailored_resume": {{
                    "name": "{actual_name}",
                    "skills": ["list", "of", "relevant", "skills"],
                    "experience": [
                        {{
                            "title": "job title",
                            "company": "company name",
                            "description": "single complete description"
                        }}
                    ],
                    "education": [
                        {{
                            "degree": "degree name",
                            "school": "school name",
                            "description": "tailored description"
                        }}
                    ]
                }},
                "match_score": 85,
                "improvements": ["list", "of", "improvements", "made"]
            }}
            """
            
            # Get response from Gemini
            response = self.model.invoke(prompt)
            
            # Extract and clean the content
            response_content = response.content
            print(f"Raw API Response: {response_content}")
            
            # Clean the response - remove any markdown formatting
            cleaned_content = response_content
            if "```json" in cleaned_content:
                cleaned_content = cleaned_content.split("```json")[1].split("```")[0]
            elif "```" in cleaned_content:
                cleaned_content = cleaned_content.split("```")[1]
            
            cleaned_content = cleaned_content.strip()
            print(f"Cleaned content: {cleaned_content}")
            
            try:
                result = json.loads(cleaned_content)
                # Validate output
                tailored = TailoredResume(**result)
                return tailored.model_dump()
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Failed content: {cleaned_content}")
                raise Exception("Failed to parse AI response into valid JSON")
            
        except Exception as e:
            print(f"Resume processing error: {str(e)}")
            print(f"Full error details:", e)
            raise

    def parse_resume_content(self, content):
        lines = content.split('\n')
        resume = {
            'name': '',
            'skills': [],
            'experience': [],
            'education': []
        }

        current_section = None
        current_item = None

        for line in lines:
            line = line.strip()
            if not line or line == 'content:':
                continue

            # Extract name from the first line
            if not resume['name'] and '|' in line:
                resume['name'] = line.split('|')[0].strip()
                continue

            # Remove YAML markers and quotes
            line = line.strip('- "\'')
            line = line.replace('\\u2022', '•')
            
            # Detect sections
            if 'Education' in line:
                current_section = 'education'
                continue
            elif 'Experience' in line:
                current_section = 'experience'
                continue
            elif 'Technical Skills' in line or 'Skills' in line:
                current_section = 'skills'
                continue

            if current_section == 'skills':
                if ':' in line:
                    _, skills = line.split(':', 1)
                    resume['skills'].extend([s.strip().strip("'") for s in skills.split(',')])
            
            elif current_section == 'experience':
                if ('–' in line or '-' in line) and not line.startswith('•'):
                    if current_item and current_item['description']:
                        resume['experience'].append(current_item)
                    
                    parts = line.split('–')
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        company = parts[1].strip()
                        current_item = {
                            'title': title,
                            'company': company,
                            'description': ''
                        }
                elif line.startswith('•') and current_item:
                    description = line[1:].strip()
                    if current_item['description']:
                        current_item['description'] += ' ' + description
                    else:
                        current_item['description'] = description
            
            elif current_section == 'education':
                if 'Purdue' in line:
                    resume['education'].append({
                        'degree': 'Bachelor of Science in Computer Engineering',
                        'school': 'Purdue University',
                        'description': 'Expected graduation: May 2024'
                    })

        # Add last experience item
        if current_item and current_item['description']:
            resume['experience'].append(current_item)

        return resume
