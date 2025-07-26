import google.generativeai as genai
import json
import re
GEMINI_API_KEY = "AIzaSyBnL7m5aIx8Jmu63jKdnvoDNY7x2nqxGLk"
FIND_SPEAKER_PROMPT = "/Users/td/Documents/GitHub/FinetunedMTLBot/prompts/find_speakers.txt"
GENERATIVE_MODEL = "gemini-2.5-flash-lite-preview-06-17"

class Gemini_Model:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GENERATIVE_MODEL)

    def get_speakers(self, paragraph):
        with open(FIND_SPEAKER_PROMPT, "r", encoding="utf-8") as f:
            prompt = f.read()
            prompt += "\n" + paragraph
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        try:
            result = json.loads(raw_text)
            return result
        except json.JSONDecodeError:
            print("Failed to parse JSON:", raw_text)
            return {}


def load_paragraphs(path, max_paragraphs=None):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Clean and split into paragraphs
    paragraphs = [p.strip().replace("\n", " ") for p in raw.split('\n\n') if p.strip()]
    return paragraphs[:max_paragraphs] if max_paragraphs else paragraphs

def format_prompt(paragraph):
    return (
        "You are a literary analyst helping build character relationship graphs from fiction.\n"
        "Given the following paragraph, extract any relationships or interactions between named characters.\n"
        "Return JSON with the structure: [{\"character_1\": str, \"character_2\": str, \"relationship\": str}]\n\n"
        f"Paragraph:\n{paragraph}"
    )

def analyze_paragraphs(model, paragraphs, limit=10):
    results = []
    for i, para in enumerate(paragraphs[:limit]):
        prompt = format_prompt(para)
        try:
            response = model.generate_content(prompt)
            print(f"\n--- Paragraph {i+1} ---\n{para}\n")
            print("Response:", response.text.strip())
            results.append(response.text.strip())
        except Exception as e:
            print(f"Error in paragraph {i+1}: {e}")
    return results

if __name__ == "__main__":
    genai.configure(api_key=GEMINI_API_KEY)

    paragraphs = load_paragraphs("/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/the_loss_of_the_swansea_extract.txt")

    model = genai.GenerativeModel("gemini-1.5-flash")  # "gemini-pro" or "gemini-1.5-pro" for stronger results

    analyze_paragraphs(model, paragraphs, limit=15)  # you can increase the limit later