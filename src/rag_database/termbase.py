
class TermBaseBuilder:
    def __init__(self, retriever, llm, glossary_list):
        self.retriever = retriever
        self.llm = llm
        self.glossary_list = glossary_list

    def build_entry(self, term, chapter=None):
        chunks = self.retriever.retrieve(f"Context for term: {term}", chapter=chapter)
        context_text = "\n\n".join([chunk.node.get_content() for chunk in chunks])
        prompt = (
            f"Glossary terms: {self.glossary_list}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Term: \"{term}\"\n\n"
            "Generate:\n"
            "- target translation\n"
            "- brief definition\n"
            "- term type\n"
            "- reference chapter\n"
        )
        response = self.llm.generate(prompt)
        return self.parse_response(response)

    def parse_response(self, resp):
        # Basic parser stub — extend as needed.
        return { line.split(":")[0].strip(): line.split(":")[1].strip() 
                 for line in resp.split("\n") if ":" in line }
