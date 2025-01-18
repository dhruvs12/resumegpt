from setuptools import setup, find_packages

setup(
    name="ResumeGPT",
    version="2.1",
    python_requires='>=3.10',
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=4.0.0",
        "pydantic>=2.7.1",
        "python-dotenv>=1.0.0",
        "uvicorn>=0.27.0",
        "asgiref>=3.7.0",
        "beautifulsoup4>=4.12.3",
        "transformers==4.36.0",
        "torch==2.1.0",
        "scikit-learn==1.3.0",
        "numpy==1.24.3",
        "sentence-transformers==2.2.2",
        "langchain-google-genai>=0.0.6"
    ],
)
