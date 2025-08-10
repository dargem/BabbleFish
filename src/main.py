import logging
import sys
import os
import json
import asyncio

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


from src.data_manager.file_manager import File_Manager
from src.entity_management.find_entities import Entity_Finder
from src.rag_database.base_rag import RAG_Database
from src.entity_management.entity_matcher_interfacer import Entity_Matcher

async def main():
    # Get project root dynamically

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    FOLDER_SOURCE = os.path.join(project_root, "data", "raw", "lotm_files")





    print("finding file paths")

    # First stage gets files
    file_manager = File_Manager(FOLDER_SOURCE)
    start_idx = 0
    end_idx = 1
    file_paths = file_manager.get_files(start_idx=start_idx, end_idx=end_idx)
    
    # Second stage construct RAG database (await async create)
    print("creating database")
    rag_database = await RAG_Database.create(file_paths, start_idx=start_idx)
    chapter_keyed_list = rag_database.retrieve_chunks()
    
    # Third stage get entities
    print("finding entities")
    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities(use_extra_gemini_ner=True)
    print(entities)
    
    # engage in entity reunification
    

    # Fourth stage use RAG to find good localisations for entry
    print("building entity entries")
    data = rag_database.build_JSON_term_entries(entities, chapter_idx=10)

    # Fifth stage build database
    print("create glossary")
    file_manager.build_glossary(data)
    
    # Retrieve semantically split input, indexed by chapter_idx and paragraph
    
    # Sixth stage replace/put markers in OG text with translated names
    
    print("inserting markers")
    glossary = file_manager.get_glossary()
    chapter_keyed_list = rag_database.retrieve_chunks() # this keys chapter_idx to a list of ordered chunks

    entity_matcher = Entity_Matcher(glossary, chapter_keyed_list)
    chapter_keyed_list = entity_matcher.get_matches()
    for key in chapter_keyed_list:
        for para in chapter_keyed_list[key]:
            print(para)

    
    '''
    entities = [entry["entity"] for entry in glossary]
    tupled_entities = [(entry["entity"],entry["description"]) for entry in glossary]

    entity_chapter_presence = { entity: [] for entity in entities } # marks chapters an entity has been found in

    # 6.1 Do an exact match through the files
    entity_chapter_presence_temp = file_manager.get_entity_chapter_presence(entities, start_idx, end_idx)
    for entity in entity_chapter_presence_temp:
        entity_chapter_presence[entity] = entity_chapter_presence_temp[entity] # merges lists together
    # 6.2 Do a lemmatised match through the files, can use Spacy


    # 6.3 Do a semantic match through the files using RAG
    rag_database.check_tupled_term_relevance(tupled_entities, start_idx = start_idx, end_idx = end_idx)
    '''
    # Seventh stage, llm to create structured out original in form of semantics

    # Eighth stage, translate using llm 


    # Further stages here...


if __name__ == "__main__":
    asyncio.run(main())
