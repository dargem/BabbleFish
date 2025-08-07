
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
                
                # Lemmatize the entire clean text for better context using SpacyLemmatizer
                try:
                    # Use SpacyLemmatizer to lemmatize the entire clean text for better context
                    lemmatized_clean_text = SpacyLemmatizer.lemmatize_text(clean_text, self.target_language)
                    
                    # Get the spaCy model for token-level processing
                    nlp = SpacyLemmatizer.models.get(SpacyLemmatizer.lingua_to_key.get(self.target_language, 'ENGLISH'))
                    if nlp is None:
                        raise ValueError(f"No model available for language {self.target_language}")
                    
                    # Process the clean text with spaCy to get token positions
                    doc = nlp(clean_text)
                    lemmatized_tokens = lemmatized_clean_text.split()
                    
                    # Create a mapping from original tokens to their lemmatized forms
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
                    
                    # Now apply lemmatized matching to the result_text
                    # Find words that haven't been tagged yet and check for lemmatized matches
                    offset = 0  # Track offset due to inserted translation tags
                    
                    for i, token in enumerate(doc):
                        if token.is_space or token.is_punct or not token.text.strip():
                            continue
                            
                        # Check if this token area already has translation tags
                        search_start = max(0, token.idx + offset - 50)  # Search window
                        search_end = min(len(result_text), token.idx + len(token.text) + offset + 50)
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
                                        return f"{match.group()} [{entity} translates to {translation}]"
                                    
                                    # Replace only the first occurrence
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