from find_entities import Entity_Finder

class EntityManager():
    '''
    A class for managing and creating entities, called by main for greater simplicity
    Should support loading from json and dynamically updating entities as new chapters are processed
    '''
    def __init__(self, entities = None):
        self.entity_finder = Entity_Finder()

    def _find_entities(self):
        self.entities = self.entity_finder.find_entities(use_extra_gemini_ner=False)