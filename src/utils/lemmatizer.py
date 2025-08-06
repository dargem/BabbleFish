# Multi-language lemmatization using spaCy
import re
from typing import Optional, Dict, List

import spacy
from spacy.lang.en import English
from spacy.lang.zh import Chinese
from spacy.lang.ja import Japanese
from spacy.lang.ko import Korean
from spacy.lang.es import Spanish
from spacy.lang.fr import French

class SpacyLemmatizer:
    models = {}
    model_names = {
        'ENGLISH': 'en_core_web_sm',
        'CHINESE': 'zh_core_web_sm', 
        'JAPANESE': 'ja_core_news_sm',
        'KOREAN': 'ko_core_news_sm',
        'SPANISH': 'es_core_news_sm',
        'FRENCH': 'fr_core_news_sm'
    }
    
    # Load spaCy models at class initialization
    for language, model_name in model_names.items():
        try:
            # Try to load the full trained model
            models[language] = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name}")
        except OSError:
            raise OSError(f"spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
    
    @staticmethod
    def lemmatize_text(text: str, language: str = 'ENGLISH'):
        # lemmatises text using spacy
        if not text:
            print("lemmatiser was called without text, likely error")
            return text
        
        if language not in SpacyLemmatizer.model_names:
            raise ValueError(f"Language {language} not supported")
            
        nlp = SpacyLemmatizer.models.get(language)
        if nlp is None:
            raise ValueError(f"No model available for language {language}")
    
        # Process the text with spaCy
        doc = nlp(text)
        
        # Extract lemmatized tokens, preserving word boundaries
        lemmatized_tokens = []
        for token in doc:
            if not token.is_space and not token.is_punct:
                # Use lemma if available, otherwise use lowercase text
                lemma = token.lemma_ if hasattr(token, 'lemma_') and token.lemma_ else token.text.lower()
                lemmatized_tokens.append(lemma)
        
        return ' '.join(lemmatized_tokens)
    
    @staticmethod
    def lemmatize_entity(entity: str, language: str = 'ENGLISH'):
        """Lemmatize a single entity"""
        return SpacyLemmatizer.lemmatize_text(entity, language)

if __name__ == "__main__":
    print("starting")
    print(SpacyLemmatizer.lemmatize_text("testing some example sentences bob skating down a hill"))