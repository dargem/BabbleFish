import sys
import os

from .models.gemini_ner_nodel import Gemini_NER_Model
from .models.hugging_ner_model import NER_Model

class OccurrenceFinder:
    '''
    Returns a hashmap of entities, keyed to the chapter
    Has the option of using gemini for further NER searching and some entity unification
    can be expensive though, lot of queries
    '''
    ner_model = NER_Model
    @staticmethod
    def find_occurrence(text):
        # For now NER only, gemini second layer elsewhere

        ner_model = OccurrenceFinder.ner_model
        occurrences = ner_model.get_entities(text)

        '''
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
        '''
        return occurrences