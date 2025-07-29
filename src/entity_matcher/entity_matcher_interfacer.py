import os

class Entity_Matcher(self):

    def __init__(self, glossary, file_paths, start_idx, semantic_matcher):
        self.glossary = glossary
        self.file_paths = file_paths
        self.start_idx = start_idx
        self.semantic_matcher = semantic_matcher

    def get_entity_chapter_presence(self, entities, start_idx, end_idx):
        # 1 do an exact match
        file_paths = self.get_files(start_idx, end_idx)
        entity_chapter_presence = {}
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path,'r', encoding="utf-8") as f:
                    txt = f.read()
                    for entity in entities:
                        if entity in txt:
                            entity_chapter_presence[entity].append(start_idx+i)
            except(FileNotFoundError, PermissionError) as e:
                print(f"Critical error: {e}")

        # 2 do a lemmatized match
        lemmatized_entities = []
        for entity in entities:
            lemmatized_entity = entity
            lemmatized_entities.append(lemmatized_entity)
        
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path,'r', encoding="utf-8") as f:
                    txt = f.read()

                    # lemmatize txt
                    lemmatize

                    for lemmatized_entity in lemmatized_entities:
                        if lemmatized_entity in txt:
                            entity_chapter_presence[entity].append(start_idx+i)
            except(FileNotFoundError, PermissionError) as e:
                print(f"Critical error: {e}")

        return entity_chapter_presence

    

    
    # 1 do an exact match

    # 2 do a lemmatized match
