import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


from folder_preprocessing.file_extractor import File_Extractor
from create_glossary.find_entities import Entity_Finder
from rag_database.rag_database_interfacer import RAG_Database

FOLDER_SOURCE = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/example_txt_list"

if __name__ == "__main__":
    # First stage gets files
    file_extractor = File_Extractor(FOLDER_SOURCE)
    file_paths = file_extractor.get_files()
    exit()
    # Second stage construct RAG database
    rag_database = RAG_Database(file_paths)
    # Third stage get entities
    print("finding entities")
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