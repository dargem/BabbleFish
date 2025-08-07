
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
                
                # Now do lemmatized matching for words that weren't already tagged
                # But first, let's identify all already tagged positions
                tagged_positions = set()
                for match in re.finditer(r'\b\w+\b(?=\s*\[[^\]]*translates to[^\]]*\])', result_text):
                    # Mark positions of words that are already tagged
                    for pos in range(match.start(), match.end()):
                        tagged_positions.add(pos)
                
                # Split into tokens while preserving whitespace and already tagged content
                tokens = re.split(r'(\s+|\[[^\]]+\])', result_text)
                new_tokens = []
                current_pos = 0
                
                for token in tokens:
                    # Skip whitespace or already tagged content
                    if not token or token.isspace() or (token.startswith('[') and token.endswith(']')):
                        new_tokens.append(token)
                        current_pos += len(token)
                        continue
                    
                    # Extract word part and punctuation
                    match = re.match(r'^(\w+)([^\w]*)$', token)
                    if match:
                        word_part, punct_part = match.groups()
                        
                        # Check if this word position is already tagged
                        word_start = current_pos
                        word_end = current_pos + len(word_part)
                        is_already_tagged = any(pos in tagged_positions for pos in range(word_start, word_end))
                        
                        if is_already_tagged:
                            new_tokens.append(token)
                            current_pos += len(token)
                            continue
                    else:
                        # If no match, just append the token as is
                        new_tokens.append(token)
                        current_pos += len(token)
                        continue
                    
                    # Skip if word_part is empty
                    if not word_part:
                        new_tokens.append(token)
                        current_pos += len(token)
                        continue
                    
                    # Try lemmatized matching
                    try:
                        lemmatized_word = SpacyLemmatizer.lemmatize_text(word_part, 'ENGLISH')
                        
                        tagged = False
                        for entity, translation in entities:
                            lemmatized_entity = lemmatizer_map.get(entity, "")
                            if lemmatized_word == lemmatized_entity:
                                #print(f"matched lemmatized words {word_part} with {entity} as {lemmatized_entity}")
                                token = f"{word_part} [lemmatized match, {entity} translates to {translation}]{punct_part}"
                                tagged = True
                                break
                        
                        if not tagged:
                            token = word_part + punct_part
                            
                    except Exception as e:
                        # If lemmatization fails, just use the original token
                        print(f"Lemmatization failed for '{word_part}': {e}")
                        token = word_part + punct_part
                    
                    new_tokens.append(token)
                    current_pos += len(token)
                
                new_segments.append(''.join(new_tokens))

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