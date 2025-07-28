# /home/user/FinetunedMTLBot/src/main.py
import logging
import sys
import os
import json

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# CORRECTED IMPORTS: Always start with 'src' because it's now the top-level package that Python can find.
from src.data_manager.file_manager import File_Manager
from src.create_glossary.find_entities import Entity_Finder
from src.rag_database.rag_database_interfacer import RAG_Database

if __name__ == "__main__":
    
    # input the folder
    FOLDER_SOURCE = "/home/user/FinetunedMTLBot/data/raw/lotm_files"
    
    # First stage gets files
    file_manager = File_Manager(FOLDER_SOURCE)

    
    file_paths = file_manager.get_files(min_index_inclusive=0,max_index_exclusive=3)
    
    # Second stage construct RAG database

    rag_database = RAG_Database(file_paths)

    # Third stage get entities
    '''
    print("finding entities")
    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities()
    for entity in entities:
        print(entity)
    
    # Fourth stage use RAG to find good localisations for entry
    terms = []
    for entity in entities:
        terms.append(rag_database.build_term_entry(entity,chapter=10))
    
    data = rag_database.build_JSON_term_entries(entities,chapter=10)

    # Fifth stage build database
    file_manager.build_glossary(data)
    '''
    # Sixth stage replace/put markers in OG text with translated names
    glossary = file_manager.get_glossary()
    entities = file_manager.get_glossary_entities()
    print(entities)
    tupled_entities = []
    for entry in glossary:
        tup = (entry["entity"],entry["description"])
        tupled_entities.append(tup)

    rag_database.check_term_relevance(entities, 1, 4)
    



    # Sixth stage LLM translation

    # Seventh stage, post processing etc