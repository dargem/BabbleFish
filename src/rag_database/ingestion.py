from src.utils.model_settings import Model_Utility_Class

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import ServiceContext, Settings
from llama_index.core import VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader
import os

class Ingestion:
    def __init__(self, file_path, llm, embedding_model_name=Model_Utility_Class.RAG_EMBEDDING_MODEL):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")
        docs = SimpleDirectoryReader(input_files=[file_path]).load_data()

        Settings.llm = llm
        service_context = ServiceContext.from_defaults(llm=Settings.llm)

        pipeline = IngestionPipeline(transformations=[
            SentenceSplitter(chunk_size=256, chunk_overlap=32),
            TitleExtractor(),
            HuggingFaceEmbedding(model_name=embedding_model_name),
        ])
        nodes = pipeline.run(docs)
        self.index = VectorStoreIndex.from_documents(nodes, service_context=service_context)

