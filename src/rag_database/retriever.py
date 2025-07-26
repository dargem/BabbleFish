from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

class Retriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, chapter=None, top_k=5):
        filters = None
        if chapter:
            filters = MetadataFilters(filters=[
                MetadataFilter(key="chapter", value=chapter, operator=FilterOperator.EQ)
            ])
        retr = self.index.as_retriever(similarity_top_k=top_k, filters=filters)
        return retr.retrieve(query)
