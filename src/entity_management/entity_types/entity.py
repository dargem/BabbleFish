class Entity():
    ''' An individual entity, not unified with aliases '''
    def __init__(self, chapter_idx):
        self.occurrences_by_chapter = {}
        self.add_occurrence(chapter_idx)

    def add_occurrence(self, chapter_idx):
        self.chapter_idx_cutoff = chapter_idx
        if chapter_idx not in self.occurrences_by_chapter:
            self.occurrences_by_chapter[chapter_idx] = 1
        else:
            self.occurrences_by_chapter[chapter_idx] += 1
    
    def update_cutoff(self, chapter_idx):
        self.chapter_idx_cutoff = chapter_idx

    '''
    def load_save(self,name,lemmatized_name,chapter_cutoff,description,term_type,mention_chapter_idx,english_target_translation):
        # load a save file, can be changed to intake json/hashmap later
        self.name = name
        self.lemmatized_name = lemmatized_name
        self.chapter_cutoff = chapter_cutoff
        self.description = description
        self.term_type = term_type
        self.mention_chapter_idx = mention_chapter_idx
        self.english_target_translation = english_target_translation
    '''