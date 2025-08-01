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
    """
    Multi-language lemmatizer using spaCy for accurate lemmatization
    """
    
    def __init__(self):
        self.models = {}
        self.model_names = {
            'ENGLISH': 'en_core_web_sm',
            'CHINESE': 'zh_core_web_sm', 
            'JAPANESE': 'ja_core_news_sm',
            'KOREAN': 'ko_core_news_sm',
            'SPANISH': 'es_core_news_sm',
            'FRENCH': 'fr_core_news_sm'
        }
        
        # Only initialize if spaCy is available
        self._load_models()
    
    def _load_models(self):
        """Load spaCy models, with fallbacks if models aren't installed"""

        for language, model_name in self.model_names.items():
            try:
                # Try to load the full model
                self.models[language] = spacy.load(model_name)
                print(f"Loaded spaCy model: {model_name}")
            except OSError:
                try:
                    # Fall back to language class without full model
                    fallback_class = self.fallback_classes.get(language)
                    if fallback_class:
                        self.models[language] = fallback_class()
                        print(f"Using spaCy language class for {language} (model {model_name} not found)")
                    else:
                        self.models[language] = None
                except Exception as e:
                    print(f"Failed to load spaCy support for {language}: {e}")
                    self.models[language] = None
    

    def lemmatize_text(self, text: str, language: Optional[str] = None) -> str:
        """
        Lemmatize text using spaCy
        
        Args:
            text: The text to lemmatize
            language: Optional language specification. If None, will auto-detect
        
        Returns:
            Lemmatized text
        """
        if not text:
            return text
        
        # Auto-detect language if not specified
        if language is None:
            language = self.detect_language(text)
             
        # Get the appropriate spaCy model
        nlp = self.models.get(language)
        if nlp is None:
            print(f"No spaCy model available for {language}, using basic lemmatization")
            return self._basic_lemmatize(text, language)
        
        try:
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
            
        except Exception as e:
            print(f"Error processing text with spaCy for {language}: {e}")
            # Fallback to basic processing
            return self._basic_lemmatize(text, language)
    
    def _basic_lemmatize(self, text: str, language: str) -> str:
        """Basic lemmatization fallback when spaCy is not available"""
        # Simple processing: extract words and lowercase them
        words = re.findall(r'\b\w+\b', text.lower())
        return ' '.join(words)
    
    def lemmatize_entity(self, entity: str, language: Optional[str] = None) -> str:
        """
        Lemmatize a single entity using spaCy
        
        Args:
            entity: The entity to lemmatize
            language: Optional language specification. If None, will auto-detect
        
        Returns:
            Lemmatized entity
        """
        return self.lemmatize_text(entity, language)
    
    def is_model_available(self, language: str) -> bool:
        """Check if a spaCy model is available for the given language"""
        return language in self.models and self.models[language] is not None


# Global lemmatizer instance
_lemmatizer = None

def _get_lemmatizer():
    """Get or create the global lemmatizer instance"""
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = SpacyLemmatizer()
    return _lemmatizer

def lemmatize_text(text: str, language: Optional[str] = None) -> str:
    """
    Lemmatize text with spaCy multi-language support
    
    Args:
        text: The text to lemmatize
        language: Optional language specification. If None, will auto-detect
    
    Returns:
        Lemmatized text
    """
    lemmatizer = _get_lemmatizer()
    return lemmatizer.lemmatize_text(text, language)

def lemmatize_entity(entity: str, language: Optional[str] = None) -> str:
    """
    Lemmatize a single entity with spaCy multi-language support
    
    Args:
        entity: The entity to lemmatize
        language: Optional language specification. If None, will auto-detect
    
    Returns:
        Lemmatized entity
    """
    lemmatizer = _get_lemmatizer()
    return lemmatizer.lemmatize_entity(entity, language)

def get_available_languages() -> List[str]:
    """Get list of languages for which spaCy models are available"""
    lemmatizer = _get_lemmatizer()
    return [lang for lang, model in lemmatizer.models.items() if model is not None]

def install_model_command(language: str) -> str:
    """Get the command to install a spaCy model for the given language"""
    lemmatizer = _get_lemmatizer()
    model_name = lemmatizer.model_names.get(language)
    if model_name:
        return f"python -m spacy download {model_name}"
    return f"No model available for language: {language}"