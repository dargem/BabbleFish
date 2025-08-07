
import os
import re
from lingua import Language, LanguageDetectorBuilder

from ..utils.lemmatizer import SpacyLemmatizer

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
        import spacy

        entities = [(entry["entity"], entry["english target translation"]) for entry in self.glossary]
        lemmatizer_map = {entry["entity"]: entry["lemmatized entity"] for entry in self.glossary}

        new_chapter_keyed_list = {}

        for chapter_idx, segments in chapter_keyed_list.items():
            new_segments = []

            for segment in segments:
                # First, try exact matches with longer entities first to prevent double matching
                result_text = segment
                
                # Sort entities by length (descending) to match longer phrases first
                for entity, translation in sorted(entities, key=lambda x: -len(x[0])):
                    # Use word boundaries to ensure we match complete words
                    pattern = r'\b' + re.escape(entity) + r'\b'
                    
                    # Replace all instances of this entity
                    def replace_match(match):
                        return f"{match.group()} [{entity} translates to {translation}]"
                    
                    result_text = re.sub(pattern, replace_match, result_text, flags=re.IGNORECASE)
                
                # Now do lemmatized matching using full context
                # First, get the clean text (without translation tags) for lemmatization
                clean_text = re.sub(r'\[[^\]]*translates to[^\]]*\]', '', result_text)
                
                # Lemmatize the entire clean text for better context
                try:
                    # Get the appropriate spaCy model for the target language
                    language_key = 'ENGLISH'  # Default to English
                    if hasattr(self, 'target_language') and self.target_language:
                        lang_map = {
                            Language.ENGLISH: 'ENGLISH',
                            Language.CHINESE: 'CHINESE', 
                            Language.JAPANESE: 'JAPANESE',
                            Language.KOREAN: 'KOREAN',
                            Language.SPANISH: 'SPANISH',
                            Language.FRENCH: 'FRENCH'
                        }
                        language_key = lang_map.get(self.target_language, 'ENGLISH')
                    
                    nlp = SpacyLemmatizer.models.get(language_key)
                    if nlp is None:
                        raise ValueError(f"No model available for language {language_key}")
                    
                    # Process the clean text with spaCy to get lemmatized tokens with positions
                    doc = nlp(clean_text)
                    
                    # Create a mapping from original word positions to lemmatized forms
                    lemma_map = {}
                    for token in doc:
                        if not token.is_space and not token.is_punct and token.text.strip():
                            lemma = token.lemma_ if hasattr(token, 'lemma_') and token.lemma_ else token.text.lower()
                            lemma_map[token.i] = {
                                'original': token.text,
                                'lemma': lemma,
                                'start': token.idx,
                                'end': token.idx + len(token.text)
                            }
                    
                    # Now apply lemmatized matching to the result_text
                    # Find words that haven't been tagged yet and check for lemmatized matches
                    clean_doc = nlp(clean_text)
                    offset = 0  # Track offset due to inserted translation tags
                    
                    for i, token in enumerate(clean_doc):
                        if token.is_space or token.is_punct or not token.text.strip():
                            continue
                            
                        # Calculate position in result_text (accounting for inserted tags)
                        original_start = token.idx
                        original_end = token.idx + len(token.text)
                        
                        # Find the corresponding position in result_text
                        # This is tricky because we've inserted translation tags
                        # Let's use a different approach: find the word in result_text
                        
                        # Check if this token area already has translation tags
                        search_start = max(0, original_start + offset - 50)  # Search window
                        search_end = min(len(result_text), original_end + offset + 50)
                        search_area = result_text[search_start:search_end]
                        
                        # Skip if this word is already tagged
                        word_pattern = r'\b' + re.escape(token.text) + r'\b(?=\s*\[[^\]]*translates to[^\]]*\])'
                        if re.search(word_pattern, search_area, re.IGNORECASE):
                            continue
                        
                        # Get lemmatized form and check for matches
                        if i in lemma_map:
                            lemma = lemma_map[i]['lemma']
                            
                            for entity, translation in entities:
                                lemmatized_entity = lemmatizer_map.get(entity, "")
                                if lemma == lemmatized_entity and lemmatized_entity:
                                    # Find and replace this specific word occurrence
                                    word_pattern = r'\b' + re.escape(token.text) + r'\b'
                                    # Only replace if not already tagged
                                    def replace_if_not_tagged(match):
                                        # Check if this match is already tagged
                                        start_pos = match.start()
                                        end_pos = match.end()
                                        # Look ahead for translation tag
                                        remaining_text = result_text[end_pos:]
                                        if remaining_text.strip().startswith('[') and 'translates to' in remaining_text:
                                            return match.group()  # Already tagged, don't replace
                                        print(f"matched lemmatized word '{token.text}' with entity '{entity}' as '{lemmatized_entity}'")
                                        exit()
                                        return f"{match.group()} [{entity} translates to {translation}]"
                                    
                                    # Replace only the first occurrence in the search area
                                    before_replacement = result_text
                                    result_text = re.sub(word_pattern, replace_if_not_tagged, result_text, count=1, flags=re.IGNORECASE)
                                    
                                    # Update offset if replacement occurred
                                    if result_text != before_replacement:
                                        offset += len(result_text) - len(before_replacement)
                                        break  # Only match one entity per word
                    
                except Exception as e:
                    print(f"Full-context lemmatization failed for segment: {e}")
                    # Fall back to original word-by-word approach if needed
                    pass
                
                new_segments.append(result_text)

            new_chapter_keyed_list[chapter_idx] = new_segments

        return new_chapter_keyed_list

    '''
    def _close_match(self, chapter_keyed_list):
        entities = [(entry["entity"], entry["english target translation"]) for entry in self.glossary]
        lemmatiser = {entry["entity"]: entry["lemmatized entity"] for entry in self.glossary}

        new_chapter_keyed_list = {}
        for chapter_idx, segments in chapter_keyed_list.items():
            new_segments = []
            for segment in segments:
                # Split on whitespace, preserving spaces and newlines
                tokens = re.split(r'(\s+)', segment)
                new_tokens = []
                for token in tokens:
                    if token.isspace():
                        new_tokens.append(token)
                        continue
                    # Separate word from punctuation (e.g. 'dragon.' → 'dragon' + '.')
                    match = re.match(r'^(\w+)([^\w]*)$', token)
                    if match:
                        word_part, punct_part = match.groups()
                    else:
                        word_part, punct_part = token, ''

                    # seperated punctuation can leave empty space
                    if not word_part:
                        continue
                    
                    tagged = False
                    for entity, translation in entities:
                        if word_part == entity:
                            token = f"{word_part} [{entity} translates to {translation}]{punct_part}"
                            tagged = True
                            break
                    
                    lemmatized_word_part = SpacyLemmatizer.lemmatize_text(word_part)

                    if not tagged:
                        for entity, translation in entities:
                            if lemmatized_word_part == lemmatiser[entity]:
                                print(f"matched lemmatized words {word_part} with {entity} as {lemmatiser[entity]}")
                                token = f"{word_part} [{entity} translates to {translation}]{punct_part}"
                                tagged = True
                                break

                    if not tagged:
                        token = word_part + punct_part

                    new_tokens.append(token)

                new_segments.append(''.join(new_tokens))

            new_chapter_keyed_list[chapter_idx] = new_segments
        return new_chapter_keyed_list
        '''