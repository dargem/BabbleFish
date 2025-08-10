import sys
import os

from .models.gemini_ner_nodel import Gemini_NER_Model
from .models.hugging_ner_model import NER_Model

class Entity_Finder:
    '''Returns a hashmap of entities, keyed to the chapter'''
    @staticmethod
    def find_entities(self, use_extra_gemini_ner, chapter_keyed_text):

        # models basically duck type, ducksafe? 
        llm_model = Gemini_NER_Model() if use_extra_gemini_ner else NER_Model()
        full_text = ""


        chapter_keyed_entities = {}
        for key in chapter_keyed_text:
            text = chapter_keyed_text[key]
            chapter_keyed_entities[key] = llm_model.get_entities(text)

        return chapter_keyed_entities