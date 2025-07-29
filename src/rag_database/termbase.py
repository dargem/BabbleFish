
class TermBaseBuilder:
    def __init__(self, retriever):
        self.retriever = retriever

    def check_term_relevance(self, entity, chapter_idx):
        nodes = self.retriever.retrieve(
            query = f"Context for term: {entity}", 
            matchType = "EQ", 
            similarity_top_k = 1, 
            chapter_idx = chapter_idx
        )
        #print("node 1")
        #print(nodes[0].get_content())
        #print("node 2")
        #print(nodes[1].get_content())
        if not nodes:
            return False
        match_strength = nodes[0].score
        match_req = 0.75
        if (match_strength > match_req):
            print(nodes[0].get_content())
        return match_strength > match_req

    def build_entry(self, entity, llm, chapter_idx=None):
        nodes = self.retriever.retrieve(
            query = f"Context for term: {entity}", 
            matchType = "LTE", 
            similarity_top_k = 10, 
            chapter_idx = chapter_idx
        )
        chunks = [node.get_content() for node in nodes]

        '''
        # for checking chunks
        if chunks:
            print(chunks[0])
            print("first chunk above")
        '''
            
        if not chunks:
            print(f"No context found for term '{entity}' with chapter filter below {chapter_idx}.")
            return {
                "long description": "No relevant context found.",
                "term type": "N/A",
                "english target translation": "N/A",
            }

        context_text = "\n\n".join(chunks)
        prompt = ( # maybe modify this prompt later
            f"Context:\n{context_text}\n\n"
            "Your task is to act as a highly knowledgeable linguist, summarising this entity for knowledge recall as part of a RAG system. "
            "Analyze the provided 'Context' thoroughly to understand the usage, nuances, and specific implications of the 'Term'. "
            "Then, for the given term, provide a detailed and comprehensive description. "
            "Ensure the description includes its primary meaning, any specific connotations or cultural relevance within the provided context, and its functional role or significance. "
            "After providing the description, give a precise and contextually appropriate English target translation. "
            "The translation MUST meticulously fit the overall context, the author's unique style, and their specific authorial intent."
            "\n\n"
            f"Term: \"{entity}\"\n\n"
            "Please output ONLY the following fields exactly as shown, nothing else. "
            "Maintain the exact field names and order. Format the output as plain text, not JSON or any other markup.\n"
            "description: [Provide a detailed, multi-sentence description based on the context. Focus on meaning, connotations, and functional role. Aim for 3-5 sentences minimum.]\n"
            "term type: [Identify the grammatical or categorical type of the term, e.g., Title, Concept, Character Name, Item, Ability, Location, Event, etc. Only one type.]\n"
            "english target translation: [Provide the most accurate and contextually appropriate English translation.]\n"
        )
        
        response = llm.complete(prompt)
        return self.parse_response(response.text, entity, chapter_idx)  # Access .text from the response object

    def parse_response(self, resp, entity, chapter_idx=None):
        """
        Parses the response text expected in the form:
        key: value
        and returns a dict {key: value}
        """
        if not isinstance(resp, str):
            print(f"WARNING: parse_response received non-string input: {type(resp)}")
            return {}

        result = {}
        result["entity"] = entity
        result["chapter cutoff"] = chapter_idx
        for line in resp.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()  # normalize keys to lowercase for consistent access
            value = value.strip()
            result[key] = value
        return result
