import google.generativeai as genai
import re
import os
from ..utils.model_settings import Model_Utility_Class

# Get project root dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

FIND_NAMED_ENTITIES_PROMPT = os.path.join(project_root, "prompts", "find_named_entities.txt")
FIND_NAMES_PROMPT = os.path.join(project_root, "prompts", "find_proper_names.txt")

# "gemini-2.5-pro"
# "gemini-2.0-flash"
class Gemini_NER_Model():
    def __init__(self):
        pass

    def get_names(self, paragraph):
        genai.configure(api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.GEMINI_NER_MODEL))
        model = genai.GenerativeModel(Model_Utility_Class.GEMINI_NER_MODEL)  
        with open(FIND_NAMES_PROMPT, "r", encoding="utf-8") as f:
            prompt = f.read()
            prompt += "\n" + paragraph
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:csv)?\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        try:
            # Split by commas and strip whitespace from each name
            names = [name.strip() for name in raw_text.split(",") if name.strip()]
            names = [name for name in names if name.lower()!="null"]
        except Exception as e:
            print(f"Failed to parse CSV: {raw_text}\nError: {e}")
            names = []

        return names
    
    def get_entities(self, text):
        genai.configure(api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.GEMINI_NER_MODEL))
        model = genai.GenerativeModel(Model_Utility_Class.GEMINI_NER_MODEL)  
        with open(FIND_NAMED_ENTITIES_PROMPT, "r", encoding="utf-8") as f:
            prompt = f.read()
            prompt += "\n" + text
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:csv)?\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        try:
            # Split by commas and strip whitespace from each name
            objects = [name.strip() for name in raw_text.split(",") if name.strip()]
            objects = [object for object in objects if object.lower()!="null"]
        except Exception as e:
            print(f"Failed to parse CSV: {raw_text}\nError: {e}")
            objects = []

        return objects