from folder_preprocessing.file_extractor import File_Extractor
from create_glossary.find_entities import Entity_Finder
from rag_database.rag_database_interfacer import RAG_Database

FOLDER_SOURCE = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/example_txt_list"

if __name__ == "__main__":
    file_extractor = File_Extractor(FOLDER_SOURCE)
    found_files = file_extractor.get_files()
    for file in found_files:
        print(file)
    exit()
    entity_finder = Entity_Finder()
    entities = entity_finder.find_Entities()

    rag_database = RAG_Database()
    