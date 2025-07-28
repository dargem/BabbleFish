import logging
import sys
import os
import json
import asyncio  # <--- import asyncio

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

    file_paths = file_manager.get_files(file_min_inclusive=1, file_max_exclusive=4)

    # Second stage construct RAG database (await async create)
    rag_database = await RAG_Database.create(file_paths)
    
    # Third stage get entities
    print("finding entities")
    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities()
    for entity in entities:
        print(entity)

    # Fourth stage use RAG to find good localisations for entry
    terms = []
    for entity in entities:
        terms.append(rag_database.build_term_entry(entity, chapter=10))

    data = rag_database.build_JSON_term_entries(entities, chapter=10)

    # Fifth stage build database
    file_manager.build_glossary(data)
    
    # Sixth stage replace/put markers in OG text with translated names
    glossary = file_manager.get_glossary()
    entities = file_manager.get_glossary_entities()
    print(entities)
    tupled_entities = []
    for entry in glossary:
        tup = (entry["entity"], entry["description"])
        tupled_entities.append(tup)

    rag_database.check_term_relevance(entities, chapter_min_inclusive = 1, chapter_max_exclusive= 4)

    # Further stages here...


if __name__ == "__main__":
    asyncio.run(main())
