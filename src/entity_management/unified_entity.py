from .entity import Entity

class UnifiedEntity():
    ''' A unified entity, contains other entities which are aliases under it'''
    def __init__(self):
        self.entity_list = [] # list of entities for management
        self.term_type = "" # all entities should have same term type

    def load_save(self,names,lemmatized_names,chapter_cutoff,description,term_type,mention_chapter_idx,english_target_translation):
        '''
        Load a save file, can be changed to intake json/hashmap later
        '''
        self.names=names
        self.lemmatized_names=lemmatized_names
        self.chapter_cutoff=chapter_cutoff
        self.description=description
        self.term_type=term_type
        self.mention_chapter_idx=mention_chapter_idx
        self.english_target_translation=english_target_translation

    def get_names(self):
        return [entity.get_name() for entity in self.entity_list]
    
    def get_lemmatized_tuples(self):
        return [entity.get_name_tuple() for entity in self.entity_list]

    def _set_names(self, name):
        pass

    def most_frequent_name(self):
        pass