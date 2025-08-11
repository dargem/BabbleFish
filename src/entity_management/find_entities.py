import sys
import os

from .models.gemini_ner_nodel import Gemini_NER_Model
from .models.hugging_ner_model import NER_Model

class Entity_Finder:
    '''
    Returns a hashmap of entities, keyed to the chapter
    Has the option of using gemini for further NER searching and some entity unification
    can be expensive though, lot of queries
    '''
    @staticmethod
    def find_entities(self, use_extra_gemini_ner, chapter_keyed_text):

        # models basically duck type, ducksafe? 
        ner_model = NER_Model()
        if use_extra_gemini_ner:
            llm_model = Gemini_NER_Model()

        chapter_keyed_entities = {}

        for key in chapter_keyed_text:
            text = chapter_keyed_text[key]
            base_ner_entities = ner_model.get_entities(text)

            if use_extra_gemini_ner:
                refined_ner_entities = llm_model.get_entities(text)
            else:
                chapter_keyed_entities[key]=base_ner_entities
                
            

        llm_model = Gemini_NER_Model() if use_extra_gemini_ner else NER_Model()
        full_text = ""



        return chapter_keyed_entities