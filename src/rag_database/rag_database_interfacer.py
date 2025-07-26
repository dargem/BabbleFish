from src.utils.model_settings import Model_Utility_Class
from src.rag_database.ingestion import Ingestion
from src.rag_database.retriever import Retriever
from src.rag_database.termbase import TermBaseBuilder

class RAG_Database:
    def __init__(self, file_path, glossary_list):
        self.ingestion = Ingestion(file_path=file_path, llm=Model_Utility_Class.RAG_RETRIEVER_MODEL)
        self.retriever = Retriever(index=self.ingestion.index)
        self.termbase = TermBaseBuilder(retriever=self.retriever, llm=Model_Utility_Class.RAG_RETRIEVER_MODEL, glossary_list=glossary_list)

    def build_term_entry(self, term, chapter=None):
        return self.termbase.build_entry(term, chapter=chapter)