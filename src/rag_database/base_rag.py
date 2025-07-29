import os
from dotenv import load_dotenv
import logging
import glob
from src.utils.model_settings import Model_Utility_Class

logger = logging.getLogger(__name__)

load_dotenv()

try:
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding
except ImportError as e:
    logger.critical(f"RAG_Database: FATAL ERROR - Missing LlamaIndex integration packages for Gemini. "
                    f"Please install: pip install llama-index-llms-gemini llama-index-embeddings-gemini. Error: {e}")
    raise

from src.rag_database.ingestion import Ingestion
from src.rag_database.retriever import Retriever
from src.rag_database.termbase import TermBaseBuilder


class RAG_Database:
    def __init__(self, ingestion, embed_model, llm):
        self.ingestion = ingestion
        self.embed_model = embed_model
        self.llm = llm
        self.index = ingestion.index
        self.retriever = Retriever(self.index)
        self.termbase = TermBaseBuilder(retriever=self.retriever)
        logger.info("RAG_Database: Initialization complete. Index and Retriever ready.")

    @classmethod
    async def create(cls, individual_file_paths: list[str], start_idx):
        logger.info("RAG_Database: Starting async create method.")

        google_api_key = os.getenv("GOOGLE_API_KEY_1")
        if not google_api_key:
            logger.critical("RAG_Database: GOOGLE_API_KEY environment variable NOT SET! Cannot initialize models.")
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it in your environment or .env file.")
        else:
            logger.info("RAG_Database: GOOGLE_API_KEY environment variable found.")

        # Setup LLM and embedding model
        try:
            llm = Gemini(model="gemini-2.5-flash-lite", api_key=google_api_key)
            embed_model = GeminiEmbedding(model_name=Model_Utility_Class.RAG_EMBEDDING_MODEL, api_key=google_api_key)
            
            # Test embedding sync call (if this is async, wrap accordingly)
            test_embed_str = "This is a small test string to verify the embedding model is working correctly."
            test_embed_val = embed_model.get_text_embedding(test_embed_str)
            
            if test_embed_val is None or not isinstance(test_embed_val, list) or len(test_embed_val) == 0:
                logger.critical("RAG_Database: Initial embedding model test FAILED!")
                raise RuntimeError("Embedding model failed to return a valid embedding.")
            else:
                logger.info(f"RAG_Database: Initial embedding model test SUCCESS. Embedding dimension: {len(test_embed_val)}.")
        except Exception as e:
            logger.critical(f"RAG_Database: FATAL ERROR during model setup: {e}", exc_info=True)
            raise

        # Prepare file metadata list
        file_metadata_list = []
        chapter_idx = start_idx # index starts at start of what paths are
        for file_path in individual_file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"RAG_Database: File path does not exist: {file_path}. Skipping.")
                continue
            file_metadata_list.append((file_path, {"chapter_idx": chapter_idx}))
            chapter_idx += 1

        if not file_metadata_list:
            logger.warning("RAG_Database: No valid files found. Creating empty ingestion.")
            ingestion = await Ingestion.create([], embed_model=embed_model)
            return cls(ingestion=ingestion, embed_model=embed_model, llm=llm)

        # Await async ingestion creation
        ingestion = await Ingestion.create(file_metadata_list=file_metadata_list, embed_model=embed_model)

        if ingestion.index is None:
            logger.critical("RAG_Database: Ingestion did not return a valid index.")
            raise RuntimeError("Ingestion pipeline failed to create a valid index.")

        return cls(ingestion=ingestion, embed_model=embed_model, llm=llm)

    # The rest of your methods remain synchronous:

    def build_term_entry(self, term, chapter_idx=None):
        self.llm = Gemini(
            model=Model_Utility_Class.RAG_RETRIEVER_MODEL,
            api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.RAG_RETRIEVER_MODEL),
            thinking_config={"thinkingBudget": -1},
        )
        return self.termbase.build_entry(term, self.llm, chapter_idx=chapter_idx)

    def build_JSON_term_entries(self, entity_list, chapter_idx=None):
        data = []
        for entity in entity_list:
            self.llm = Gemini(
                model=Model_Utility_Class.RAG_RETRIEVER_MODEL,
                api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.RAG_RETRIEVER_MODEL),
                thinking_config={"thinkingBudget": -1},
            )
            data.append(self.termbase.build_entry(entity, self.llm, chapter_idx=chapter_idx))
        return data

    '''
    def check_term_relevance(self, entities, chapter_min_inclusive, chapter_max_exclusive):
        dic = {}
        for entity in entities:
            dic[entity] = []
            for i in range(chapter_min_inclusive, chapter_max_exclusive):
                if self.termbase.check_term_relevance(entity, chapter=i):
                    dic[entity].append(i)
            print(dic[entity])
        print(dic)
    '''

    def check_tupled_term_relevance(self, tupled_entities, start_idx, end_idx):
        dic = {}
        for entity_tuple in tupled_entities:
            entity = entity_tuple[0]
            description = entity_tuple[1]
            dic[entity] = []
            combined_term = "entity: " + entity + ", description: " + description
            for i in range(start_idx, end_idx):
                if self.termbase.check_term_relevance(combined_term, chapter_idx=start_idx+i):
                    dic[entity].append(start_idx+i)
            print(dic[entity])
        print(dic)
