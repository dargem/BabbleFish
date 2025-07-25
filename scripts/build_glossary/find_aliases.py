# This builds a glossary through extracting terms creating the dictionary for consistent translation, e.g. names

import sys
import os
import json
sys.path.append('/Users/td/Documents/GitHub/FinetunedMTLBot')

from alias_merger import AliasMerger
from models.gemini.gemini_model import Gemini_Model
from models.ner.ner_model import NERModel
INPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/raw_text_extract.txt"
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/glossary/character_dictionary.json"

def create_Glossary_File():
    llm_model = Gemini_Model()
    ner_model = NERModel()
    alias_merger = AliasMerger()

    # stage 1 extracts names, increase paragraphs per list entry size for less queries if using llm
    paragraphs_per_list_entry=1 # might want to increase for llm
    paragraphs = get_paragraph_list(paragraphs_per_list_entry)
    dic_names = get_names_model(ner_model,paragraphs) # can sub for llm model also
    print(dic_names)
    # this creates a dic of names with frequency

    base_names = {}
    for key in dic_names:
        base_names[key]=[] # dictionary list of aliases
    
    # stage 2 uses extracted names pairing with aliases
    paragraphs_per_list_entry = 1
    paragraphs = get_paragraph_list(paragraphs_per_list_entry)
    for index, para in enumerate(paragraphs):
        lm_dict = llm_model.get_speakers(para)
        lm_dict = {
            name: [f"{alias} (Paragraph {index})" for alias in aliases]
            for name, aliases in lm_dict.items()
        }
        print(lm_dict)
        alias_merger.add_aliases(lm_dict)

    merged_aliases = alias_merger.merge()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged_aliases, f, indent=2, ensure_ascii=False)
    
def get_names_model(model, paragraphs):
    dic_names={}
    for para in paragraphs:
        names = model.get_names(para)
        for name in names:
            dic_names.setdefault(name, {"Frequency": 0})
            dic_names[name]["Frequency"] += 1
    return dic_names

def get_paragraph_list(paragraphs_per_list_entry):
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        raw = f.read()

    paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]
    n = paragraphs_per_list_entry
    paragraphs = [''.join(paragraphs[i:i+n]) for i in range(0, len(paragraphs) - len(paragraphs) % n, n)]
    return paragraphs

if __name__ == "__main__":
    create_Glossary_File()
    print("finished")