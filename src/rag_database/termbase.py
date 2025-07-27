# from src.utils.model_settings import Model_Utility_Class # No longer strictly needed if llm is from Settings
from llama_index.core import Settings

class TermBaseBuilder:
    def __init__(self, retriever):
        self.retriever = retriever

    def build_entry(self, term, chapter=None):
        chunks = self.retriever.retrieve(f"Context for term: {term}", chapter=chapter)
        
        if not chunks:
            print(f"No context found for term '{term}' with chapter filter below {chapter}.")
            return {
                "english target translation": "N/A",
                "brief definition": "No relevant context found.",
                "term type": "N/A",
                "reference chapter": "N/A"
            }

        context_text = "\n\n".join(chunks)
        prompt = (
            f"Context:\n{context_text}\n\n"
            f"Term: \"{term}\"\n\n"
            "Generate:\n"
            "- english target translation\n"
            "- brief definition\n"
            "- term type\n"
        )
        
        # Use Settings.llm directly
        response = Settings.llm.complete(prompt) 
        return self.parse_response(response.text) # Access .text from response object

    def parse_response(self, resp):
        # Basic parser stub — extend as needed.
        # Ensure resp is a string
        if not isinstance(resp, str):
            print(f"WARNING: parse_response received non-string input: {type(resp)}")
            return {} # Or handle as error
            
        result = {}
        for line in resp.split("\n"):
            if ":" in line:
                parts = line.split(":", 1) # Split only on the first colon
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else "" # Handle cases with no value after colon
                result[key] = value
        return result