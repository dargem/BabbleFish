from .entity import Entity

class UnifiedEntity():
    ''' 
    A unified entity, contains other entities which are aliases under it
    '''
    def __init__(self):
        self.entity_list = [] # list of entities for management
        self.term_type = "" # all entities should have same term type

    def load_save(self):
        '''
        Load a save file from prob a json
        '''

    def get_names(self):
        return [entity.name for entity in self.entity_list]
    
    def get_lemmatized_tuples(self):
        return [(entity.name, entity.lemmatized_name) for entity in self.entity_list]