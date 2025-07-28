# src/rag_database/ingestion.py

import os
import aiofiles
import asyncio

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.embeddings import BaseEmbedding 
from llama_index.core.node_parser import SemanticSplitterNodeParser

from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

from src.utils.model_settings import Model_Utility_Class


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
            node_parser = SemanticSplitterNodeParser.from_defaults(
                embed_model=GeminiEmbedding(
                    model_name=Model_Utility_Class.RAG_EMBEDDING_MODEL,
                    api_key=Model_Utility_Class.get_next_key(Model_Utility_Class.RAG_EMBEDDING_MODEL),
                ),
                include_metadata=True,
                include_prev_next_rel=True,
            )
            split_nodes = await asyncio.to_thread(node_parser.get_nodes_from_documents, [raw_doc])
            nodes.extend(split_nodes)

        if not nodes:
            return cls(VectorStoreIndex(nodes=[], embed_model=embed_model))

        # Generate embeddings in parallel
        async def embed_node(node):
            embedding = await asyncio.to_thread(
                embed_model.get_text_embedding,
                node.get_content(metadata_mode="all")
            )
            node.embedding = embedding
            return node

        embedded_nodes = await asyncio.gather(*(embed_node(node) for node in nodes))
        return cls(VectorStoreIndex(nodes=embedded_nodes, embed_model=embed_model))