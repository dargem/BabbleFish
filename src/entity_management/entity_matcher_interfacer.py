
import os
import re
from lingua import Language, LanguageDetectorBuilder

from ..data_manager.lemmatizer import SpacyLemmatizer

class Entity_Matcher:
    def __init__(self, glossary, chapter_keyed_list):
        self.chapter_keyed_list = chapter_keyed_list
        self.glossary = glossary
        languages = [Language.ENGLISH, Language.CHINESE, Language.JAPANESE, Language.KOREAN, Language.SPANISH, Language.FRENCH] 
        # can add more later, what space has curently
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        rand_chap = ""
        # will just take a random one to detect, this is single language documents so doesn't matter
        for segment in next(iter(chapter_keyed_list.values())):
            rand_chap += segment
        self.target_language = detector.detect_language_of(rand_chap)
    
    def get_matches(self):
        holder = self.chapter_keyed_list
        holder = self._close_match(holder)
        return holder

    def _close_match(self, chapter_keyed_list):
        entities = [(entry["entity"], entry["english target translation"]) for entry in self.glossary]
        lemmatizer_map = {entry["entity"]: entry["lemmatized entity"] for entry in self.glossary}

        new_chapter_keyed_list = {}

        for chapter_idx, segments in chapter_keyed_list.items():
            new_segments = []

            for segment in segments:
                result_text = segment
                
                # First, try exact matches with longer entities first to prevent double matching
                # Sort entities by length (descending) to match longer phrases first
                for entity, translation in sorted(entities, key=lambda x: -len(x[0])):
                    # Use the new find_entity_matches function for better multilingual support
                    matches = SpacyLemmatizer.find_entity_matches(result_text, entity, self.target_language)
                    
                    # Replace matches from right to left to preserve positions
                    for start, end in reversed(matches):
                        # Check if this position is already tagged
                        before_match = result_text[:start]
                        after_match = result_text[end:]
                        
                        # Skip if already tagged (check for translation markers nearby)
                        if ('[' in after_match[:50] and 'translates to' in after_match[:100]) or \
                           ('[' in before_match[-50:] and 'translates to' in before_match[-100:]):
                            continue
                        
                        matched_text = result_text[start:end]
                        replacement = f"{matched_text} [{entity} translates to {translation}]"
                        result_text = result_text[:start] + replacement + result_text[end:]
                
                # Now do lemmatized matching for words that weren't already tagged
                try:
                    # Get clean text without translation tags for lemmatization
                    clean_text = re.sub(r'\[[^\]]*translates to[^\]]*\]', '', result_text)
                    
                    # Lemmatize the entire clean text for better context
                    lemmatized_clean_text = SpacyLemmatizer.lemmatize_text(clean_text, self.target_language)
                    
                    # Get spaCy model for token processing
                    nlp = SpacyLemmatizer.models.get(SpacyLemmatizer.lingua_to_key.get(self.target_language, 'ENGLISH'))
                    if nlp is None:
                        raise ValueError(f"No model available for language {self.target_language}")
                    
                    # Process clean text and create lemma mapping
                    doc = nlp(clean_text)
                    lemmatized_tokens = lemmatized_clean_text.split()
                    
                    lemma_map = {}
                    lemma_index = 0
                    for token in doc:
                        if not token.is_space and not token.is_punct and token.text.strip():
                            if lemma_index < len(lemmatized_tokens):
                                lemma_map[token.i] = {
                                    'original': token.text,
                                    'lemma': lemmatized_tokens[lemma_index],
                                    'start': token.idx,
                                    'end': token.idx + len(token.text)
                                }
                                lemma_index += 1
                    
                    # Apply lemmatized matching
                    offset = 0  # Track offset due to inserted translation tags
                    
                    for i, token in enumerate(doc):
                        if token.is_space or token.is_punct or not token.text.strip():
                            continue
                            
                        # Check if this word is already tagged
                        search_start = max(0, token.idx + offset - 50)
                        search_end = min(len(result_text), token.idx + len(token.text) + offset + 50)
                        search_area = result_text[search_start:search_end]
                        
                        # Skip if word is already tagged - more comprehensive check
                        if re.search(r'\b' + re.escape(token.text) + r'\b\s*\[[^\]]*translates to[^\]]*\]', search_area, re.IGNORECASE):
                            continue
                        
                        # Check lemmatized form for matches
                        if i in lemma_map:
                            lemma = lemma_map[i]['lemma']
                            
                            for entity, translation in entities:
                                lemmatized_entity = lemmatizer_map.get(entity, "")
                                if lemma == lemmatized_entity and lemmatized_entity:
                                    # Use find_entity_matches for consistent matching
                                    word_matches = SpacyLemmatizer.find_entity_matches(result_text, token.text, self.target_language)
                                    
                                    if word_matches:
                                        # Take the first match that's not already tagged
                                        for match_start, match_end in word_matches:
                                            # Check more thoroughly if this position is already tagged
                                            before_text = result_text[:match_start]
                                            after_text = result_text[match_end:]
                                            
                                            # Skip if there's a translation marker nearby
                                            if ('translates to' in after_text[:100]) or \
                                               ('translates to' in before_text[-100:]):
                                                continue
                                                
                                            print(f"matched lemmatized word '{token.text}' with entity '{entity}' as '{lemmatized_entity}'")
                                            matched_text = result_text[match_start:match_end]
                                            replacement = f"{matched_text} [{entity} translates to {translation}]"
                                            result_text = result_text[:match_start] + replacement + result_text[match_end:]
                                            offset += len(replacement) - len(matched_text)
                                            break
                                        break  # Only match one entity per word
                    
                except Exception as e:
                    print(f"Full-context lemmatization failed for segment: {e}")
                    pass
                
                new_segments.append(result_text)

            new_chapter_keyed_list[chapter_idx] = new_segments

        return new_chapter_keyed_list