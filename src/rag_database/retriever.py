from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.core import Settings # Good practice to explicitly import Settings

class Retriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, chapter=None):
        filters = []

        if chapter is not None:
            # THIS IS THE KEY CHANGE: Use FilterOperator.LT for "less than"
            filters.append(
                MetadataFilter(key="chapter", operator=FilterOperator.LT, value=chapter)
            )
            # If you meant "less than or equal to", it would be FilterOperator.LTE
            # filters.append(
            #     MetadataFilter(key="chapter", operator=FilterOperator.LTE, value=chapter)
            # )

        # Pass the filters to the retriever
        retriever_instance = self.index.as_retriever(
            similarity_top_k=10,
            filters=MetadataFilters(filters=filters) if filters else None
        )
        
        nodes = retriever_instance.retrieve(query)
        
        # Add debugging print statements to confirm what's being retrieved
        if not nodes:
            print(f"WARNING: No nodes found for query '{query}' with chapter filter (LT) '{chapter}'")
            return [] # Return an empty list if no nodes found

        print(f"DEBUG: Retrieved {len(nodes)} nodes for query '{query}' with chapter filter (LT) '{chapter}'.")
        for i, node in enumerate(nodes):
            print(f"  Node {i+1} - ID: {node.id_}, Chapter: {node.metadata.get('chapter')}, Score: {node.score:.2f}")

        # Ensure you return the content for your TermBaseBuilder
        # The .retrieve() method returns a list of NodeWithScore objects,
        # so you need to access the actual node and then its content.
        return [node.node.get_content() for node in nodes] # Access node.node.get_content()