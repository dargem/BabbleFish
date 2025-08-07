# Multi-language lemmatization using spaCy
import re
from typing import Optional, Dict, List, Union

import spacy
from spacy.lang.en import English
from spacy.lang.zh import Chinese
from spacy.lang.ja import Japanese
from spacy.lang.ko import Korean
from spacy.lang.es import Spanish
from spacy.lang.fr import French
from lingua import Language

class SpacyLemmatizer:
    models = {}
    model_names = {
        'ENGLISH': 'en_core_web_lg',
        'CHINESE': 'zh_core_web_lg', 
        'JAPANESE': 'ja_core_news_lg',
        'KOREAN': 'ko_core_news_lg',
        'SPANISH': 'es_core_news_lg',
        'FRENCH': 'fr_core_news_lg'
    }
    
    # Map lingua Language enum to our language keys
    lingua_to_key = {
        Language.ENGLISH: 'ENGLISH',
        Language.CHINESE: 'CHINESE', 
        Language.JAPANESE: 'JAPANESE',
        Language.KOREAN: 'KOREAN',
        Language.SPANISH: 'SPANISH',
        Language.FRENCH: 'FRENCH'
    }
    
    # Load spaCy models at class initialization
    for language_key, model_name in model_names.items():
        try:
            # Try to load the full trained model
            models[language_key] = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name}")
        except OSError:
            raise OSError(f"spaCy model '{model_name}' not found. Install with: python -m spacy download {model_name}")
    
    @staticmethod
    def lemmatize_text(text: str, language: Union[str, Language]):
        # lemmatises text using spacy
        if not text:
            print("lemmatiser was called without text, likely error")
            return text
        
        # Convert lingua Language enum to string key if needed
        if isinstance(language, Language):
            language_key = SpacyLemmatizer.lingua_to_key.get(language, 'ENGLISH')
        else:
            language_key = language

        if language_key not in SpacyLemmatizer.model_names:
            raise ValueError(f"Language {language_key} not supported")

        nlp = SpacyLemmatizer.models.get(language_key)
        if nlp is None:
            raise ValueError(f"No model available for language {language_key}")
    
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
    def lemmatize_entity(entity: str, language: Union[str, Language] = 'ENGLISH'):
        """Lemmatize a single entity"""
        return SpacyLemmatizer.lemmatize_text(entity, language)
    
    @staticmethod
    def find_entity_matches(text: str, entity: str, language: Union[str, Language]):
        """
        Returns list of match positions (start, end) for entity in text.
        For CJK languages, uses spaCy tokenization instead of regex.
        """
        cjk_langs = [Language.CHINESE, Language.JAPANESE, Language.KOREAN]
        
        # Convert lingua Language enum to string key if needed
        if isinstance(language, Language):
            language_key = SpacyLemmatizer.lingua_to_key.get(language, 'ENGLISH')
            is_cjk = language in cjk_langs
        else:
            language_key = language
            # For string keys, check if it's a CJK language
            cjk_keys = ['CHINESE', 'JAPANESE', 'KOREAN']
            is_cjk = language_key in cjk_keys

        spacy_model = SpacyLemmatizer.models.get(language_key)
        matches = []

        if is_cjk:
            if spacy_model is None:
                raise ValueError(f"spaCy model required for CJK matching, but no model available for {language_key}")
            
            # Use spaCy tokenization for CJK languages
            doc = spacy_model(text)
            for token in doc:
                if token.text == entity:
                    matches.append((token.idx, token.idx + len(token.text)))
        else:
            # Use regex word boundaries for non-CJK languages
            pattern = r'\b' + re.escape(entity) + r'\b'
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                matches.append((match.start(), match.end()))

        return matches


if __name__ == "__main__":
    print("starting")
    test_text = "testing some example sentences bob skating down a hill"
    print(f"Original: {test_text}")
    print(f"Lemmatized: {SpacyLemmatizer.lemmatize_text(test_text, Language.ENGLISH)}")
    
    # Test find_entity_matches
    test_matches = SpacyLemmatizer.find_entity_matches(test_text, "skating", Language.ENGLISH)
    print(f"Matches for 'skating': {test_matches}")
    
    # Test Chinese text if available
    chinese_text = "我喜欢学习中文"
    try:
        chinese_lemma = SpacyLemmatizer.lemmatize_text(chinese_text, Language.CHINESE)
        print(f"Chinese original: {chinese_text}")
        print(f"Chinese lemmatized: {chinese_lemma}")
    except Exception as e:
        print(f"Chinese test failed: {e}")