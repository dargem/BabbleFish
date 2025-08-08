# src/rag_database/ingestion.py

import os
import aiofiles
import asyncio
import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.embeddings import BaseEmbedding 
from llama_index.core.node_parser import SemanticSplitterNodeParser


from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google.genai.types import EmbedContentConfig


try:
    from ..utils.model_settings import Model_Utility_Class
except ImportError:
    from src.utils.model_settings import Model_Utility_Class

logger = logging.getLogger(__name__)

import time
from datetime import datetime

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}", flush=True)

class Ingestion:
    def __init__(self, index):
        self.index = index

    @classmethod
    async def create(cls, file_metadata_list, embed_model: BaseEmbedding):
        raw_docs = []

        # Load Raw Documents asynchronously
        for file_path, metadata in file_metadata_list:
            if not os.path.exists(file_path):
                continue
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    if not content.strip():
                        continue
                    raw_docs.append(Document(text=content, metadata=metadata))
            except Exception:
                continue

        if not raw_docs:
            return cls(VectorStoreIndex(nodes=[], embed_model=embed_model))

        # Split and embed nodes
        nodes = []
        for raw_doc in raw_docs:
            log(f"starting semantic splitting for raw_doc")
            node_parser = SemanticSplitterNodeParser.from_defaults(
                embed_model = GoogleGenAIEmbedding(
                    model_name = Model_Utility_Class.RAG_EMBEDDING_MODEL, 
                    api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.RAG_EMBEDDING_MODEL),
                    embedding_config=EmbedContentConfig(
                        output_dimensionality=768, ## can decrease later
                        task_type = "SEMANTIC_SIMILARITY"
                    )
                ),
                breakpoint_percentile_threshold=85, # this takes an int out of 100, default 95, decrease to make finer
                include_metadata=True,
                include_prev_next_rel=True,
                buffer_size=0
            )
            split_nodes = await asyncio.to_thread(node_parser.get_nodes_from_documents, [raw_doc])
            nodes.extend(split_nodes)
            log(f"finished semantic splitting for raw_doc")

        if not nodes:
            return cls(VectorStoreIndex(nodes=[], embed_model=embed_model))

        api_call_count = 0

        # Generate embeddings in parallel
        async def embed_node(node):
            nonlocal api_call_count
            api_call_count += 1
            current_call = api_call_count
            log(f"Sending embedding API call #{current_call}")
            start_time = time.time()
            embedding = await asyncio.to_thread(
                embed_model.get_text_embedding,
                node.get_content(metadata_mode="all")
            )
            elapsed = time.time() - start_time
            node.embedding = embedding
            log(f"Received response for API call #{current_call} (took {elapsed:.2f}s)")
            return node

        print("starting to send api calls")
        embedded_nodes = await asyncio.gather(*(embed_node(node) for node in nodes))

        logger.info(f"Ingestion: Sent {api_call_count} embedding API calls.")
        print(f"Ingestion: Sent {api_call_count} embedding API calls.")
        return cls(VectorStoreIndex(nodes=embedded_nodes, embed_model=embed_model))
