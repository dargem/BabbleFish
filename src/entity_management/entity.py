class Entity():
    ''' An individual entity, not unified with aliases '''
    def __init__(self):
        self.name = ""
        self.lemmatized_name = ""
        self.chapter_cutoff = 0 # how far ahead this chapter is
        self.description = "" # description of the entity
        self.term_type = "" # the type of entity, is it a person object etc
        self.mention_chapter_idx = {} # a hash of occurrences, key is chapter, value num appearances
        self.english_target_translation = "" # target translation
        self.total_occurrences = 0 # how many occurrences the entity has in the text

    def load_save(self,name,lemmatized_name,chapter_cutoff,description,term_type,mention_chapter_idx,english_target_translation):
        # load a save file, can be changed to intake json/hashmap later
        
        self.name = name
        self.lemmatized_name = lemmatized_name
        self.chapter_cutoff = chapter_cutoff
        self.description = description
        self.term_type = term_type
        self.mention_chapter_idx = mention_chapter_idx
        self.english_target_translation = english_target_translation

    def get_name(self):
        return self.name
    
    def get_name_tuple(self):
        return (self.name,self.lemmatized_name)