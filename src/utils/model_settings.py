# availablemodel s
'''
model list

gemini-2.5-pro
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-2.0-flash
gemini-2.0-flash-lite

gemini-2.5-flash-lite-preview-06-17
gemini-live-2.5-flash-preview

'''


class Model_Utility_Class:
    # static class for setups, what models to use for what etc
    # Embedding model
    RAG_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

    # For quering the termbase on terms
    RAG_RETRIEVER_MODEL = "gemini-2.0-flash-lite"

    # For finding what terms to enter termbase
    GEMINI_NER_MODEL = "gemini-2.5-pro"

    # For translation
    GEMINI_TRANSLATION_MODEL = "gemini-2.5-pro"

    # For back checking, implement later...
    



