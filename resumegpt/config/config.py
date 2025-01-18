import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_MODEL_NAME = os.getenv('GOOGLE_AI_MODEL', 'gemini-1.5-pro')
    GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
    API_URL = 'http://localhost:5000/api'

