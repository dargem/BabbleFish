import google.generativeai as genai
import json
import re
from src.utils.model_settings import Model_Utility_Class

try:
    from .ner_interface import NER_Model_Interface
except ImportError:
    from ner_interface import NER_Model_Interface

FIND_NAMED_ENTITIES_PROMPT = "/home/user/FinetunedMTLBot/prompts/find_named_entities.txt"
FIND_NAMES_PROMPT = "/home/user/FinetunedMTLBot/prompts/find_proper_names.txt"

# "gemini-2.5-pro"
# "gemini-2.0-flash"
class Gemini_NER_Model(NER_Model_Interface):
    def __init__(self):
        pass

    def get_names(self, paragraph):
        genai.configure(api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.GEMINI_NER_MODEL))
        self.model = genai.GenerativeModel(Model_Utility_Class.GEMINI_NER_MODEL)  
        with open(FIND_NAMES_PROMPT, "r", encoding="utf-8") as f:
            prompt = f.read()
            prompt += "\n" + paragraph
            response = self.model.generate_content(prompt)
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
    
    def get_entities(self, paragraph):
        genai.configure(api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.GEMINI_NER_MODEL))
        self.model = genai.GenerativeModel(Model_Utility_Class.GEMINI_NER_MODEL)  
        with open(FIND_NAMED_ENTITIES_PROMPT, "r", encoding="utf-8") as f:
            prompt = f.read()
            prompt += "\n" + paragraph
            response = self.model.generate_content(prompt)
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
    


