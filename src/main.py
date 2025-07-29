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
from src.create_glossary.find_entities import Entity_Finder
from src.rag_database.rag_database_interfacer import RAG_Database


async def main():
    FOLDER_SOURCE = "/home/user/FinetunedMTLBot/data/raw/lotm_files"

    # First stage gets files
    file_manager = File_Manager(FOLDER_SOURCE)
    start_idx = 0
    end_idx = 7
    file_paths = file_manager.get_files(start_idx=start_idx, end_idx=end_idx)
    # Second stage construct RAG database (await async create)
    rag_database = await RAG_Database.create(file_paths)
    
    # Third stage get entities
    print("finding entities")
    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities()
    for entity in entities:
        print(entity)

    # Fourth stage use RAG to find good localisations for entry
    data = rag_database.build_JSON_term_entries(entities, chapter_idx=10)

    # Fifth stage build database
    file_manager.build_glossary(data)
    
    # Sixth stage replace/put markers in OG text with translated names
    glossary = file_manager.get_glossary()
    entities = file_manager.get_glossary_entities()
    
    # 6.1 Do an exact match through the files

    # 6.2 Do a lemmatised match through the files, can use Spacy

    # 6.3 Do a semantic match through the files using RAG


    print(entities)

    tupled_entities = []
    for entry in glossary:
        tup = (entry["entity"], entry["description"])
        tupled_entities.append(tup)

    rag_database.check_tupled_term_relevance(tupled_entities, start_idx = start_idx, end_idx = end_idx)


    # Further stages here...


if __name__ == "__main__":
    asyncio.run(main())
