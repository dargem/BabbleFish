import os
import json
import re
from collections import defaultdict
import logging

class FileManager():
    def __init__(self, directory_path, start_idx):
        self.logger = logging.getLogger(__name__)
        # Get project root dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        
        # Constructs list of files
        file_list = self._find_files(directory_path)
        
        # Sort files by chapter number
        sorted_files = self._sort_files_by_chapter(file_list)

        # Create chapter indexed dictionary
        self.chapter_dic = self._create_chapter_dic(sorted_files, start_idx)

        # Find language
        self.language = self._detect_language()

        # Lemmatise using found language
        self.lemmatized_chapter_dic = self._create_lemmatized_chapter_dic()

        # Chunk by paragraphs and use coreference resolution if available
        self.resolved_chunked_chapter_dic = self._resolve_chunk_chapter_dic()
    
    def _find_files(self,directory_path):
        '''
        Find the files from the given directory
        '''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        
        file_list = []
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith(".txt"):
                    file_list.append(os.path.join(directory_path, filename))
        except (FileNotFoundError, PermissionError) as e:
            print(f"Critical error: {e}")
        return file_list

    def _sort_files_by_chapter(self, file_list):
        """
        Sort files by chapter number extracted from filename.
        """
        def extract_chapter_number(file_path):
            filename = os.path.basename(file_path)
            
            # Pattern 1: Extract numbers from filename (e.g., lotm1.txt -> 1)
            numbers = re.findall(r'\d+', filename)
            if numbers:
                # Take the first number found, assuming it's the chapter number
                return int(numbers[0])
            
            # Pattern 2: If no numbers found, sort alphabetically
            return float('inf')  # Put files without numbers at the end
        
        try:
            sorted_files = sorted(file_list, key=extract_chapter_number)
            print(f"Sorted {len(sorted_files)} files by chapter number")
            return sorted_files
        except Exception as e:
            print(f"Warning: Failed to sort files by chapter, using alphabetical sort: {e}")
            return sorted(file_list)

    def _create_chapter_dic(self, sorted_files, start_idx):
        '''
        chapters indexed by chapter index
        '''
        chapter_dic = {}
        for i, file in enumerate(sorted_files):
            with open(file,'r',encoding='UTF-8') as f:
                self.chapter_dic[start_idx+i] = f.read()
        return chapter_dic
    
    def _resolve_chunk_chapter_dic(self):
        '''
        Coreference resolution if available + chunking
        '''
        chunked_chapter_dic = self._chunk_chapter_dic(self.chapter_dic)
        from coreference_resolver import CoreferenceResolver
        if CoreferenceResolver.model_available(self.language):
            resolved_chunked_chapter_dic = self._chunk_chapter_dic(self.chapter_dic)
            pass
        else:
            self.logger.warning(
                f"No coreference resolution available for {self.language} language proceeding as usual without. May result in worse triplet extraction"
            )
            # system is still compatable without coreference resolution
            return chunked_chapter_dic
        
    def _chunk_chapter_dic(self,chapter_dic):
        return {key:value.split("\n\n") for key,value in chapter_dic.items()}

    def _detect_language(self):
        '''
        Builds a language detector and detects from that list
        '''
        from lingua import Language, LanguageDetectorBuilder

        languages = [
            Language.ENGLISH, 
            Language.CHINESE, 
            Language.JAPANESE, 
            Language.KOREAN, 
            Language.SPANISH, 
            Language.FRENCH
        ]

        detector = LanguageDetectorBuilder.from_languages(*languages).build()

        chapter = next(iter(self.chapter_dic.values()))

        return detector.detect_language_of(chapter)

    def _create_lemmatized_chapter_dic(self):
        from lemmatizer import SpacyLemmatizer

        lemmatized_chapter_dic = {}
        for key in self.chapter_dic:
            lemmatized_chapter_dic[key] = SpacyLemmatizer.lemmatize_text(self.chapter_dic[key])
        return lemmatized_chapter_dic