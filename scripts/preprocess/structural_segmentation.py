# Sentence/Dialogue Splitting and speaker tagging of the raw
# Probably outputs a json
import re
import json
import os
import sys
sys.path.append('/Users/td/Documents/GitHub/FinetunedMTLBot')

INPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/raw_text_extract.txt"
OUTPUT_PATH = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/preprocessed/structurally_segmented.json"

# Detects a line of dialogue using quotation marks
def create_Dialogue_Segments(paragraph, chapter_index, para_index):
    """
    Splits a paragraph into alternating narration and dialogue blocks,
    preserving quotation marks and sequence.
    
    Returns a list of dicts with keys: 'type' (dialogue/narration) and 'text'.
    """
    # Combine common quote types into one pattern
    pattern = r'(“[^”]+”|"[^"]+"|‘[^’]+’|\'[^\']+\')'

    segments = []
    last_end = 0
    segment_index = 0

    for match in re.finditer(pattern, paragraph):
        start, end = match.span()
        if start > last_end:
            # Text before dialogue = narration
            narration = paragraph[last_end:start].strip()
            if narration:
                segments.append({
                    'type': 'narration',
                    'text': narration,
                    'meta': {
                        'chapter_index': chapter_index,
                        'paragraph_index': para_index,
                        'segment_index': segment_index,
                    }
                })  
            segment_index+=1

        dialogue = match.group().strip()
        if dialogue:
                segments.append({
                    'type': 'dialogue',
                    'text': dialogue,
                    'meta': {
                        'chapter_index': chapter_index,
                        'paragraph_index': para_index,
                        'segment_index': segment_index,
                    }
                })
                segment_index+=1
        last_end = end

    # Capture any trailing narration after last quote
    if last_end < len(paragraph):
        narration = paragraph[last_end:].strip()
        if(narration):
            segments.append({
                'type': 'narration',
                'text': narration,
                'meta': {
                    'chapter_index': chapter_index,
                    'paragraph_index': para_index,
                    'segment_index': segment_index,
                }
            })  
    return segments

def preprocess_file(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        raw = f.read()

    paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]
    paragraphs = [p.replace("\n"," ") for p in paragraphs]
    output = []
    
    chapter_index = 1 # placeholder for now

    for para_index, para in enumerate(paragraphs):
        para_segments = create_Dialogue_Segments(para, chapter_index, para_index)
        output.append(para_segments)

    return output

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    structured = preprocess_file(INPUT_PATH)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump(structured, out, ensure_ascii=False, indent=2)
    print(f"Preprocessing complete. Output saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

