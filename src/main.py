# /home/user/FinetunedMTLBot/src/main.py
import logging
import sys
import os

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..')) # Correct: 'main.py' is in 'src', so '..' goes to 'FinetunedMTLBot'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# CORRECTED IMPORTS: Always start with 'src' because it's now the top-level package that Python can find.
from src.folder_preprocessing.file_extractor import File_Extractor
from src.create_glossary.find_entities import Entity_Finder
from src.rag_database.rag_database_interfacer import RAG_Database

FOLDER_SOURCE = "/home/user/FinetunedMTLBot/data/raw/example_txt_list"

if __name__ == "__main__":
    # First stage gets files
    file_extractor = File_Extractor(FOLDER_SOURCE)
    file_paths = file_extractor.get_files()
    # Second stage construct RAG database
    rag_database = RAG_Database(file_paths)
    # Third stage get entities
    print("finding entities")
    exit()
    entity_finder = Entity_Finder(file_paths)
    entities = entity_finder.find_entities()
    for entity in entities:
        print(entity)
    # Fourth stage use RAG to find good localisations for entry
    terms = []
    entities = entities[0:20]
    for entity in entities:
        terms.append(rag_database.build_term_entry(entity,chapter=10))

    for term in terms:
        print(term)
    print("done!")
    # Fifth stage replace/put markers in OG text with translated names

    # Sixth stage LLM translation

    # Seventh stage, post processing etc