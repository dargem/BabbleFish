import os

try:
    from ..models.spacy.lemmatization import lemmatize_text, lemmatize_entity
except ImportError:
    from models.spacy.lemmatization import lemmatize_text, lemmatize_entity

class Entity_Matcher:
    def __init__(self, glossary, file_paths, start_idx, semantic_matcher, target_language=None):
        self.glossary = glossary
        self.file_paths = file_paths  # Already trimmed to proper files
        self.start_idx = start_idx
        self.semantic_matcher = semantic_matcher
        self.target_language = target_language

    def get_files(self, start_idx, end_idx):
        """Get file paths for the specified range of indices"""
        # Since file_paths is already trimmed, we need to adjust indexing
        relative_start = max(0, start_idx - self.start_idx)
        relative_end = min(len(self.file_paths) - 1, end_idx - self.start_idx)
        return self.file_paths[relative_start:relative_end + 1]

    def exact_match(self, entities, start_idx, end_idx):
        """Perform exact string matching for entities in text files"""
        file_paths = self.get_files(start_idx, end_idx)
        entity_chapter_presence = {}
        
        # Initialize empty lists for all entities
        for entity in entities:
            entity_chapter_presence[entity] = []
        
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    txt = f.read()
                    for entity in entities:
                        if entity in txt:
                            chapter_idx = start_idx + i
                            entity_chapter_presence[entity].append(chapter_idx)
            except (FileNotFoundError, PermissionError) as e:
                print(f"Critical error in exact_match: {e}")
        
        return entity_chapter_presence

    def lemmatized_match(self, entities, start_idx, end_idx):
        """Perform lemmatized matching for entities in text files with multi-language support"""
        file_paths = self.get_files(start_idx, end_idx)
        entity_chapter_presence = {}
        
        # Initialize empty lists for all entities
        for entity in entities:
            entity_chapter_presence[entity] = []
        
        # Lemmatize entities with language support
        lemmatized_entities = {}
        for entity in entities:
            try:
                lemmatized_entity = lemmatize_entity(entity, self.target_language)
                lemmatized_entities[entity] = lemmatized_entity
                print(f"Lemmatized '{entity}' -> '{lemmatized_entity}' (language: {self.target_language or 'auto-detect'})")
            except Exception as e:
                print(f"Error lemmatizing entity '{entity}': {e}")
                lemmatized_entities[entity] = entity.lower().strip()  # fallback to lowercase
        
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    txt = f.read()
                    
                    # Lemmatize the text with language support
                    try:
                        lemmatized_txt = lemmatize_text(txt, self.target_language)
                    except Exception as e:
                        print(f"Error lemmatizing text from {file_path}: {e}")
                        lemmatized_txt = txt.lower()  # fallback to lowercase
                    
                    for entity in entities:
                        lemmatized_entity = lemmatized_entities[entity]
                        if lemmatized_entity and lemmatized_entity in lemmatized_txt:
                            chapter_idx = start_idx + i
                            entity_chapter_presence[entity].append(chapter_idx)
            except (FileNotFoundError, PermissionError) as e:
                print(f"Critical error in lemmatized_match: {e}")
        
        return entity_chapter_presence

    def get_entity_chapter_presence(self, entities, start_idx, end_idx):
        """Combined method that performs both exact and lemmatized matching"""
        # Initialize empty lists for all entities
        entity_chapter_presence = {}
        for entity in entities:
            entity_chapter_presence[entity] = []
        
        print(f"Processing entities for chapters {start_idx} to {end_idx} with language: {self.target_language or 'auto-detect'}")
        
        # 1. Do exact match
        exact_matches = self.exact_match(entities, start_idx, end_idx)
        
        # 2. Do lemmatized match
        lemmatized_matches = self.lemmatized_match(entities, start_idx, end_idx)
        
        # Combine results (remove duplicates)
        for entity in entities:
            combined_chapters = list(set(
                exact_matches[entity] + lemmatized_matches[entity]
            ))
            entity_chapter_presence[entity] = sorted(combined_chapters)
            
            # Debug output
            exact_count = len(exact_matches[entity])
            lemma_count = len(lemmatized_matches[entity])
            total_count = len(entity_chapter_presence[entity])
            print(f"Entity '{entity}': {exact_count} exact matches, {lemma_count} lemmatized matches, {total_count} total unique chapters")
        
        return entity_chapter_presence
