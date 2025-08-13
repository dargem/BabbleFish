from find_entities import OccurrenceFinder
from title_pronoun_filter import NERFilter
from .entity_types.entity import Entity
# option to use LingMess for more accuracy, from fastcoref

class EntityManager():
    '''
    A class for managing and creating entities, called by main for greater simplicity
    Should support loading from json and dynamically updating entities as new chapters are processed
    Entity is an object of a class, contains occurrences of the entity
    '''
    def __init__(self, chapter_dic, lemmatized_chapter_dic, language, use_extra_gemini_ner, extensive_filter = False):
        self.occurrence_finder = OccurrenceFinder()

        # Find entities through running NER over base and lemmatised 
        base_entities_dic = self._find_entities(text_dic=chapter_dic)
        lemmatized_entities_dic = self._find_entities(text_dic=lemmatized_chapter_dic)

        # Renove pronouns and titles which are mistakes
        base_entities_dic = self._remove_pronouns_titles(base_entities_dic, language, extensive_filter)
        lemmatized_entities_dic = self._remove_pronouns_titles(lemmatized_entities_dic, language, extensive_filter)

        # Coreference resolution steps

        # entity unifier



    def _find_entities(self, text_dic):
        '''
        Finds occurrences and turns them into a hashmap of entity objects keyed by name
        '''
        entity_dic = {}
        largest_idx = 0
        for chapter_idx in text_dic:
            text = text_dic[chapter_idx]
            occurrences = self.occurrence_finder.find_occurrence(text)
            for occurrence in occurrences:
                if occurrence not in entity_dic:
                    # newly found occurrence is an entity
                    entity_dic[occurrence] = Entity(entity_dic[occurrence], chapter_idx)
                else:
                    entity_dic[occurrence].add_occurrence(chapter_idx)
            if chapter_idx > largest_idx:
                largest_idx = chapter_idx
        for value in entity_dic.values():
            value.update_cutoff(chapter_idx)
        return entity_dic
    
    def _remove_pronouns_titles(self, entity_dic, language, extensive_filter):
        return {entity: entity_dic[entity] 
                for entity 
                in entity_dic 
                if NERFilter.isRemovable(entity, language, extensive_filter)}
    
