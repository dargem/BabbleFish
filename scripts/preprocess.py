# Sentence/Dialogue Splitting and speaker tagging of the raw
# Probably outputs a json
import numpy as np
import re
import json
import os
import sys
sys.path.append('/Users/td/Documents/GitHub/FinetunedMTLBot')

from models.coref.coref_model import CorefResolver
from models.ner.ner_model import NERModel


INPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/the_loss_of_the_swansea_extract.txt"
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/preprocessed/the_loss_of_the_swansea.json"



# Detects a line of dialogue using quotation marks
def is_dialogue(segment):
    return segment["type"] == "dialogue"


# Guess speaker if they are mentioned on the same or following line
def guess_speaker(paragraphs, idx):
    if idx + 1 < len(paragraphs):
        next_line = paragraphs[idx + 1]
        match = re.search(r'(?:said|asked|whispered|muttered|replied)\s+(\w+)', next_line, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def create_Dialogue_Segments(paragraph):
    """
    Splits a paragraph into alternating narration and dialogue blocks,
    preserving quotation marks and sequence.
    
    Returns a list of dicts with keys: 'type' (dialogue/narration) and 'text'.
    """
    # Combine common quote types into one pattern
    pattern = r'(“[^”]+”|"[^"]+"|‘[^’]+’|\'[^\']+\')'

    segments = []
    last_end = 0

    for match in re.finditer(pattern, paragraph):
        start, end = match.span()
        if start > last_end:
            # Text before dialogue = narration
            narration = paragraph[last_end:start].strip()
            if narration:
                segments.append({'type': 'narration', 'text': narration})
        
        dialogue = match.group().strip()
        if dialogue:
            segments.append({'type': 'dialogue', 'text': dialogue})

        last_end = end

    # Capture any trailing narration after last quote
    if last_end < len(paragraph):
        narration = paragraph[last_end:].strip()
        if narration:
            segments.append({'type': 'narration', 'text': narration})

    return segments

def create_Larger_Segments(paragraph, min_length=50):
    """
    Splits paragraph into alternating narration and dialogue blocks,
    then groups adjacent blocks of same type into larger chunks.

    Args:
        paragraph (str): Full paragraph text.
        min_length (int): Minimum character length for segments (to help NER).

    Returns:
        List[Dict]: [{'type': 'dialogue'|'narration', 'text': str}, ...]
    """
    # Detect quoted dialogue segments
    pattern = r'(“[^”]+”|"[^"]+"|‘[^’]+’|\'[^\']+\')'

    raw_segments = []
    last_end = 0

    for match in re.finditer(pattern, paragraph):
        start, end = match.span()
        if start > last_end:
            narration = paragraph[last_end:start].strip()
            if narration:
                raw_segments.append({'type': 'narration', 'text': narration})

        dialogue = match.group().strip()
        if dialogue:
            raw_segments.append({'type': 'dialogue', 'text': dialogue})

        last_end = end

    # Catch trailing narration
    if last_end < len(paragraph):
        narration = paragraph[last_end:].strip()
        if narration:
            raw_segments.append({'type': 'narration', 'text': narration})

    # === Merge adjacent same-type segments to form larger context ===
    merged_segments = []
    buffer = ""
    last_type = None

    for seg in raw_segments:
        if seg['type'] == last_type:
            buffer += " " + seg['text']
        else:
            if buffer:
                merged_segments.append({'type': last_type, 'text': buffer.strip()})
            buffer = seg['text']
            last_type = seg['type']

    # Flush final buffer
    if buffer:
        merged_segments.append({'type': last_type, 'text': buffer.strip()})

    # === Optional: Recombine short segments ===
    final_segments = []
    for seg in merged_segments:
        if final_segments and len(seg['text']) < min_length and final_segments[-1]['type'] == seg['type']:
            final_segments[-1]['text'] += " " + seg['text']
        else:
            final_segments.append(seg)

    return final_segments

def preprocess_file(input_file, coref_model, ner_model):
    with open(input_file, "r", encoding="utf-8") as f:
        raw = f.read()

    paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]
    paragraphs = [p.replace("\n"," ") for p in paragraphs]
    output = []

    for idx, para in enumerate(paragraphs):
        para_segments = create_Larger_Segments(para)

        for segment in para_segments:
            text = segment["text"]
            # Run NER on the segment text itself (dialogue or narration)
            ner_results = ner_model.extract_entities(text)

            # Optional: run coref on the entire paragraph, or per segment depending on your needs
            # For now, just empty or skip for per segment
            clusters = []

            entry = {
                "type": segment["type"],
                "text": text,
                "named_entities": ner_results,
                "coref_clusters": clusters,
            }

            if is_dialogue(segment):
                entry["speaker_guess"] = guess_speaker(paragraphs, idx)

            output.append(entry)

    return output


def convert(o):
    if isinstance(o, (np.float32, np.float64)):
        return float(o)
    if isinstance(o, (np.int32, np.int64)):
        return int(o)
    return str(o)  # fallback to string

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    coref = CorefResolver()
    ner = NERModel()
    structured = preprocess_file(INPUT_PATH, coref, ner)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump(structured, out, ensure_ascii=False, indent=2, default = convert)

    print(f"Preprocessing complete. Output saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

