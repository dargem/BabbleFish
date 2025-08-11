import pandas as pd
from collections import defaultdict
from lingua import Language

class NERFilter():
    '''
    A utility class that contains titles and pronouns
    Used for filtering NER to get rid of these non entities
    '''

    # consider moving this to a utility class
    lingua_to_key = {
        Language.ENGLISH: 'ENGLISH',
        Language.CHINESE: 'CHINESE', 
        Language.JAPANESE: 'JAPANESE',
        Language.KOREAN: 'KOREAN',
        Language.SPANISH: 'SPANISH',
        Language.FRENCH: 'FRENCH'
    }

    name_df = pd.read_csv("language_titles_pronouns.csv")

    base_name_map = defaultdict(set)
    for _, row in name_df.iterrows():
        base_name_map[row["Language"]].add(row["Word"])

    extensive_name_df = pd.read_csv("extensive_language_titles_pronouns.csv")
    extensive_name_map = defaultdict(set)
    for _, row in extensive_name_df.iterrows():
        extensive_name_map[row["Language"]].add(row["Word"])

    @staticmethod
    def isRemovable(word, language=None, extensive_filter=False):
        used_map =(
            NERFilter.base_name_map
            if extensive_filter 
            else NERFilter.extensive_name_map
        )

        if language:
            if language in NERFilter.lingua_to_key:
                language = NERFilter.lingua_to_key[language]
            return word in used_map[language]
        else:
            for key in used_map:
                if word in used_map[key]:
                    return True
        
        return False
    
    