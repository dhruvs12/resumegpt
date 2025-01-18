from functools import lru_cache
from transformers import pipeline, AutoTokenizer, AutoModel

class ModelCache:
    @lru_cache(maxsize=None)
    def get_ner_pipeline():
        return pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        
    @lru_cache(maxsize=None)
    def get_sentiment_pipeline():
        return pipeline("sentiment-analysis")
        
    @lru_cache(maxsize=None)
    def get_transformer_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        return tokenizer, model 