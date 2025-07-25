# takes segmented narration and voice from structurally_segmented.json, adding sentiment analysis
import sys
import os
import json
sys.path.append('/Users/td/Documents/GitHub/FinetunedMTLBot')

from models.ner.ner_model import NERModel

INPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/preprocessed/structurally_segmented.json"
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/preprocessed/structurally_segmented.json"

# redone for now will be done in place later
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/preprocessed/metadata_attribution.json"


def conduct_metadata_analysis():
    ner_model = NERModel()

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        segments = json.load(f)  # segments: List[List[Dict]]

    for sublist in segments:
        for segment_data in sublist:
            text = segment_data["text"]
            sentiment = ner_model.get_entities(text)
            segment_data["meta"] = sentiment

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    return segments

if __name__ == "__main__":
    conduct_metadata_analysis()
    print("done")