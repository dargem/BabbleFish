import sys
import os

from src.models.ner.gemini_ner_model import Gemini_NER_Model

class Entity_Finder:
    def __init__(self, file_paths):
        self.file_paths = file_paths

    def find_entities(self):
        llm_model = Gemini_NER_Model()
        full_text = ""

        for path in self.file_paths:
            if not os.path.exists(path):
                print(f"Warning: {path} does not exist. Skipping.")
                continue
            with open(path, "r", encoding="utf-8") as f:
                full_text += f.read() + "\n\n"

        entities = llm_model.get_entities(full_text)
        return entities

if __name__ == "__main__":
    file_paths = [
        "data/raw/raw_text_extract.txt",
    ]

    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities()

    print("Extracted Entities:")
    for entity in entities:
        print(entity)