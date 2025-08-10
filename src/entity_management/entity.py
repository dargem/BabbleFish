class Entity():
    def __init__(self):
        self.names = [] # list of names, aliases etc
        self.lemmatized_names = [] # name list lemmatised, could be name tuple also
        self.description = "" # description of the entity
        self.term_type = "" # the type of entity, is it a person object etc
        self.mention_chapter_idx = [] # a list of mentions by idx
        self.english_target_translation = [] # target translation

    def load_save(self,names,lemmatized_names,description,term_type,mention_chapter_idx,english_target_translation):
        '''
        Load a save file, can be changed to intake json/hashmap later
        '''
        self.names=names
        self.lemmatized_names=lemmatized_names
        self.description=description
        self.term_type=term_type
        self.mention_chapter_idx=mention_chapter_idx
        self.english_target_translation=english_target_translation

    def _set_names(self, name):
        pass

    def most_frequent_name(self):
        pass