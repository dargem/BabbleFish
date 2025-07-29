from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

class Retriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, matchType, similarity_top_k, chapter_idx=None):
        if matchType != "LT" and matchType != "LTE" and matchType != "EQ":
            raise ValueError("Invalid matchType. Must be 'LT' or 'LTE' or 'EQ'.")

        filters = []

        if chapter_idx is not None:
            match(matchType):
                case "LT": 
                    filters.append(MetadataFilter(key="chapter_idx", operator=FilterOperator.LT, value=chapter_idx))
                case "LTE": 
                    filters.append(MetadataFilter(key="chapter_idx", operator=FilterOperator.LTE, value=chapter_idx))
                case "EQ":
                    filters.append(MetadataFilter(key="chapter_idx", operator=FilterOperator.EQ, value=chapter_idx))
                case _:
                    raise ValueError("Invalid matchType. Must be 'LT' or 'LTE' or 'EQ.")

        # Pass the filters to the retriever
        retriever_instance = self.index.as_retriever(
            similarity_top_k=similarity_top_k,
            filters=MetadataFilters(filters=filters) if filters else None
        )
        
        nodes = retriever_instance.retrieve(query)
        
        if not nodes:
            print(f"WARNING: No nodes found for query '{query}' with chapter_idx '{chapter_idx}'")
            return [] #Empty list if no nodes found

        print(f"DEBUG: Retrieved {len(nodes)} nodes for query '{query}' with chapter_idx '{chapter_idx}'.")
        for i, node in enumerate(nodes):
            print(f"  Node {i+1} - ID: {node.id_}, Chapter_idx: {node.metadata.get('chapter')}, Score: {node.score:.2f}")
        return nodes
        #return [node.node.get_content() for node in nodes]