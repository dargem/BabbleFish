class RelationManager():
    '''
    A class that manages the extraction of entity relationships from text
    '''
    def __init__(self, para_chunked_chapter_dic, language, unified_entities):
        self.para_chunked_chapter_dic = para_chunked_chapter_dic
        self.language = language
        self.unified_entities = unified_entities

        
