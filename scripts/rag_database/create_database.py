from llama_index.core import VectorStoreIndex, Document
from llama_index.embedding import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, MetadataExtractor

import os

def create_database():
    file_path = "/Users/td/Documents/GitHub/FinetunedMTLBot/data/raw/raw_text_extract.txt"

    if os.path.exists(file_path):
        print(f"The path '{file_path}' exists.")
    else:
        print(f"The path '{file_path}' does not exist. Please check the path.")
        exit()

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
    )

    Settings.llm = Gemini(api_key="AIzaSyBnL7m5aIx8Jmu63jKdnvoDNY7x2nqxGLk", model="gemini-2.0-flash")

    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()

    retriever = index.as_retriever()
    '''
    retrieved_docs = retriever.retrieve("")
    for i, doc in enumerate(retrieved_docs):
        print(f"Chunk {i}:\n{doc.text}\n{'-'*40}")
    '''

    response = query_engine.query("What is the role of term [placeholder]")
    print(response)
