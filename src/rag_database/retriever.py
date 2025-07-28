from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

class Retriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, matchType, similarity_top_k, chapter=None):
        if matchType != "LT" and matchType != "LTE" and matchType != "EQ":
            raise ValueError("Invalid matchType. Must be 'LT' or 'LTE' or 'EQ'.")

        filters = []

        if chapter is not None:
            match(matchType):
                case "LT": 
                    filters.append(MetadataFilter(key="chapter", operator=FilterOperator.LT, value=chapter))
                case "LTE": 
                    filters.append(MetadataFilter(key="chapter", operator=FilterOperator.LTE, value=chapter))
                case "EQ":
                    filters.append(MetadataFilter(key="chapter", operator=FilterOperator.EQ, value=chapter))
                case _:
                    raise ValueError("Invalid matchType. Must be 'LT' or 'LTE' or 'EQ.")

        # Pass the filters to the retriever
        retriever_instance = self.index.as_retriever(
            similarity_top_k=similarity_top_k,
            filters=MetadataFilters(filters=filters) if filters else None
        )
        
        nodes = retriever_instance.retrieve(query)
        
        if not nodes:
            print(f"WARNING: No nodes found for query '{query}' with chapter filter (LT) '{chapter}'")
            return [] #Empty list if no nodes found

        print(f"DEBUG: Retrieved {len(nodes)} nodes for query '{query}' with chapter filter (LT) '{chapter}'.")
        for i, node in enumerate(nodes):
            print(f"  Node {i+1} - ID: {node.id_}, Chapter: {node.metadata.get('chapter')}, Score: {node.score:.2f}")
        return nodes
        #return [node.node.get_content() for node in nodes]