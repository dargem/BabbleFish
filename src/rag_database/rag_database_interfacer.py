# src/rag_database/rag_database_interfacer.py

import os
from dotenv import load_dotenv
import logging
import glob 

logger = logging.getLogger(__name__)

load_dotenv() 

from llama_index.core import Settings
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
    # --- CHANGE: Accept a list of individual file_paths directly ---
    def __init__(self, individual_file_paths: list[str]): 
        logger.info("RAG_Database: Initializing RAG_Database instance.")
        logger.debug(f"RAG_Database: Received individual_file_paths: {individual_file_paths}")

        # 1. API Key Validation
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.critical("RAG_Database: GOOGLE_API_KEY environment variable NOT SET! Cannot initialize models.")
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it in your environment or .env file.")
        else:
            logger.info("RAG_Database: GOOGLE_API_KEY environment variable found.")

        # 2. LLM and Embedding Model Setup
        try:
            logger.info("RAG_Database: Attempting to set Settings.llm (Gemini)...")
            Settings.llm = Gemini(model="gemini-2.0-flash-lite", api_key=google_api_key)
            logger.info(f"RAG_Database: Settings.llm set to {Settings.llm.model}.")
            
            logger.info("RAG_Database: Attempting to set Settings.embed_model (GeminiEmbedding)...")
            Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=google_api_key)
            logger.info(f"RAG_Database: Settings.embed_model set to {Settings.embed_model.model_name}.")
            
            test_embed_str = "This is a small test string to verify the embedding model is working correctly."
            logger.info(f"RAG_Database: Performing a test embedding for: '{test_embed_str[:60]}...'")
            test_embed_val = Settings.embed_model.get_text_embedding(test_embed_str)

            if test_embed_val is None or not isinstance(test_embed_val, list) or len(test_embed_val) == 0:
                logger.critical(f"RAG_Database: Initial embedding model test FAILED! Returned: {test_embed_val}. "
                                f"This indicates a problem with the embedding model setup or API key/rate limits.")
                raise RuntimeError("Embedding model failed to return a valid embedding.")
            else:
                logger.info(f"RAG_Database: Initial embedding model test SUCCESS. Embedding dimension: {len(test_embed_val)}.")

        except Exception as e:
            logger.critical(f"RAG_Database: FATAL ERROR during LLM or Embedding model setup: {e}", exc_info=True)
            raise 

        # 3. Prepare File Metadata List for Ingestion
        file_metadata_list = []
        # --- CHANGE: Iterate directly over the provided list of file paths ---
        processed_files_count = 0
        
        if not individual_file_paths:
            logger.warning("RAG_Database: No individual file paths provided. Creating an empty index.")
        
        chapter_counter = 1 # Simple chapter assignment for now
        for file_path in individual_file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"RAG_Database: Provided file path does not exist: {file_path}. Skipping.")
                continue

            file_metadata_list.append((file_path, {"chapter": chapter_counter}))
            chapter_counter += 1
            processed_files_count += 1
            logger.debug(f"RAG_Database: Prepared file {file_path} with metadata {{'chapter': {chapter_counter-1}}}")

        if processed_files_count == 0:
            logger.warning("RAG_Database: No valid files were found from the provided list. Creating an empty index.")
            self.ingestion = Ingestion([]) # Pass empty list to Ingestion
            self.index = self.ingestion.index
            self.retriever = Retriever(self.index)
            self.termbase = TermBaseBuilder(retriever=self.retriever)
            return


        # 4. Initialize Ingestion Pipeline
        logger.info("RAG_Database: Initializing Ingestion component with prepared file list.")
        self.ingestion = Ingestion(file_metadata_list=file_metadata_list)
        
        self.index = self.ingestion.index
        if self.index is None:
            logger.critical("RAG_Database: Ingestion did not return a valid index. Aborting.")
            raise RuntimeError("Ingestion pipeline failed to create a valid index.")

        # 5. Initialize Retriever and Termbase
        logger.info("RAG_Database: Initializing Retriever component.")
        self.retriever = Retriever(self.index)
        
        logger.info("RAG_Database: Initializing Termbase component.")
        self.termbase = TermBaseBuilder(retriever=self.retriever)
        
        logger.info("RAG_Database: Initialization complete. Index and Retriever ready.")

    def build_term_entry(self, term, chapter=None):
        return self.termbase.build_entry(term, chapter=chapter)
