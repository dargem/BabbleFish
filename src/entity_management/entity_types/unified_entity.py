from .entity import Entity

class UnifiedEntity():
    ''' 
    A unified entity, contains other entities which are aliases under it
    '''
    def __init__(self, entity):
        self.entity_list = [] # list of entities for management
        self.term_type = "" # all entities should have same term type
        self.entity_list.append(entity)

    def add_like_entity(self, entity):
        self.entity_list.append(entity)

    

    '''
    def load_save(self,entity):
        #Load a save file from prob a json

    def get_names(self):
        return [entity.name for entity in self.entity_list]
    
    def get_lemmatized_tuples(self):
        return [(entity.name, entity.lemmatized_name) for entity in self.entity_list]
    '''