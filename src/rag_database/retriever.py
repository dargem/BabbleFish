from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

class Retriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, chapter=None):
        filters = []

        if chapter is not None:
            # for less than the filteroperator
            filters.append(
                MetadataFilter(key="chapter", operator=FilterOperator.LT, value=chapter)
            )
            # for less than or equal use LTE

        # Pass the filters to the retriever
        retriever_instance = self.index.as_retriever(
            similarity_top_k=10,
            filters=MetadataFilters(filters=filters) if filters else None
        )
        
        nodes = retriever_instance.retrieve(query)
        
        if not nodes:
            print(f"WARNING: No nodes found for query '{query}' with chapter filter (LT) '{chapter}'")
            return [] #Empty list if no nodes found

        print(f"DEBUG: Retrieved {len(nodes)} nodes for query '{query}' with chapter filter (LT) '{chapter}'.")
        for i, node in enumerate(nodes):
            print(f"  Node {i+1} - ID: {node.id_}, Chapter: {node.metadata.get('chapter')}, Score: {node.score:.2f}")

        return [node.node.get_content() for node in nodes]