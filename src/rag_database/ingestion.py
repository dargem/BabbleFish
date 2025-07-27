# src/rag_database/ingestion.py

import os
import logging

# LlamaIndex core components
# from llama_index.core.ingestion import IngestionPipeline # Still not using IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter # <-- UNCOMMENT THIS
# from llama_index.core.extractors import TitleExtractor
from llama_index.core import Settings 
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document, TextNode 
from llama_index.core.embeddings import BaseEmbedding 

logger = logging.getLogger(__name__)

class Ingestion:
    def __init__(self, file_metadata_list):
        logger.info("Ingestion: Starting document loading and processing for splitting and embedding.")
        raw_docs = [] # Renamed to raw_docs for clarity

        if not file_metadata_list:
            logger.warning("Ingestion: file_metadata_list is empty. No documents to process. Creating an empty index.")
            self.index = VectorStoreIndex([])
            return

        # 1. Load Raw Documents
        for file_path, metadata in file_metadata_list:
            if not os.path.exists(file_path):
                logger.error(f"Ingestion: File not found at path: {file_path}. Skipping this file.")
                continue 
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip(): 
                        logger.warning(f"Ingestion: File {file_path} is empty or contains only whitespace. Skipping.")
                        continue
                    raw_docs.append(Document(text=content, metadata=metadata))
                    logger.info(f"Ingestion: Loaded raw document from {file_path} (length: {len(content)} chars) with metadata: {metadata}")
            except Exception as e:
                logger.error(f"Ingestion: Error reading file {file_path}: {e}. Skipping this file.", exc_info=True)
                continue

        if not raw_docs:
            logger.warning("Ingestion: No valid raw documents were loaded. Creating an empty index.")
            self.index = VectorStoreIndex([])
            return

        logger.info(f"Ingestion: Successfully loaded {len(raw_docs)} raw documents for splitting and embedding.")

        for i, doc in enumerate(raw_docs):
            logger.debug(f"Raw Document {i+1} content length: {len(doc.text)}. Content (first 200 chars): '{doc.text[:200]}'")
            logger.debug(f"Raw Document {i+1} metadata: {doc.metadata}")

        # --- IMPORTANT CHANGE: Initialize and apply SentenceSplitter manually ---
        nodes = []
        try:
            # Initialize the SentenceSplitter
            # Recommended chunk_size: 512, 1024, or 2048. Overlap helps maintain context.
            # Using 1024 for demonstration. You can fine-tune this later.
            node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=32)
            logger.info(f"Ingestion: Initialized SentenceSplitter with chunk_size={node_parser.chunk_size}, chunk_overlap={node_parser.chunk_overlap}.")

            logger.info("Ingestion: Applying SentenceSplitter to raw documents to create nodes.")
            for i, raw_doc in enumerate(raw_docs):
                # Apply the splitter to each raw document
                split_nodes_from_doc = node_parser.get_nodes_from_documents([raw_doc])
                nodes.extend(split_nodes_from_doc)
                logger.debug(f"Ingestion: Document {i+1} split into {len(split_nodes_from_doc)} nodes.")
                # Verify metadata is passed
                if split_nodes_from_doc:
                    logger.debug(f"First node from Document {i+1} has metadata: {split_nodes_from_doc[0].metadata}")


            logger.info(f"Ingestion: Finished splitting. Total {len(nodes)} nodes created across all documents.")

            if not nodes:
                logger.warning("Ingestion: SentenceSplitter created 0 nodes. This is unexpected.")
                self.index = VectorStoreIndex([])
                return

            # --- Existing Manual Embedding Process (will now run on the split nodes) ---
            embed_model: BaseEmbedding = Settings.embed_model 

            if embed_model is None:
                logger.critical("Ingestion: Settings.embed_model is not set! Cannot generate embeddings for nodes.")
                self.index = VectorStoreIndex([])
                raise RuntimeError("Embedding model is not initialized. Ensure RAG_Database sets Settings.embed_model correctly.")

            logger.info(f"Ingestion: Manually generating embeddings for {len(nodes)} created nodes.")
            
            for i, node in enumerate(nodes):
                try:
                    # Use get_content(metadata_mode="all") to ensure all relevant text (including metadata if configured) is embedded
                    node_embedding = embed_model.get_text_embedding(node.get_content(metadata_mode="all")) 
                    
                    if node_embedding is None or not isinstance(node_embedding, list) or len(node_embedding) == 0:
                        logger.error(f"Ingestion: Failed to get embedding for node {i+1} (Node ID: {node.id_}). Returned: {node_embedding}. Skipping this node.")
                        raise RuntimeError(f"Failed to embed node {node.id_}. Check API key, model availability, or rate limits.")
                    
                    node.embedding = node_embedding
                    logger.debug(f"Ingestion: Embedded node {i+1} (ID: {node.id_}) with embedding (dim: {len(node.embedding)}).")
                except Exception as e:
                    logger.error(f"Ingestion: Error embedding node {i+1} (ID: {node.id_}): {e}", exc_info=True)
                    raise 

            logger.info(f"Ingestion: Successfully embedded {len(nodes)} nodes.")
            
            logger.info("Ingestion: Creating VectorStoreIndex from manually created and embedded nodes.")
            self.index = VectorStoreIndex(nodes=nodes) 
            logger.info("Ingestion: VectorStoreIndex created successfully.")

        except Exception as e:
            logger.critical(f"Ingestion: FATAL ERROR during node splitting, embedding, or index creation: {e}", exc_info=True)
            self.index = VectorStoreIndex([]) 
            raise