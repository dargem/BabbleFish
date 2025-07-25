# This builds a glossary through extracting terms creating the dictionary for consistent translation, e.g. names

import sys
import os
import json
sys.path.append('/Users/td/Documents/GitHub/FinetunedMTLBot')

from models.ner.gemini_ner_model import Gemini_NER_Model
from models.ner.ner_model import NERModel
INPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/raw_text_extract.txt"
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/glossary/character_dictionary.json"

def find_Entities():
    llm_model = Gemini_NER_Model()
    # ner_model = NERModel()

    # Can just feed the whole chapter into either NER models
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        chapter = f.read()

    list_objects = llm_model.get_entities(chapter)
    return list_objects

if __name__ == "__main__":
    print(find_Entities())