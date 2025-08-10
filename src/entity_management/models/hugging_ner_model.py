from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

class NER_Model():
    def __init__(self, model_name="dslim/bert-base-NER"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy="max")

    def _chunk_text(self, text, max_tokens=400, stride=50):
        """
        Splits text into overlapping chunks using character-based approach first,
        then validates with tokenizer. This avoids tokenizing very long texts upfront.
        """
        # Handle empty or very short text
        if not text or len(text.strip()) < 10:
            return [text] if text else []
        
        # Use character-based chunking first (rough estimate: ~4 chars per token)
        max_chars = max_tokens * 4
        stride_chars = stride * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get character-based chunk
            end = min(start + max_chars, len(text))
            char_chunk = text[start:end]
            
            # Validate and adjust chunk size using tokenizer
            tokens = self.tokenizer(char_chunk, add_special_tokens=False, return_tensors=None)['input_ids']
            
            # If chunk is too long, reduce it
            while len(tokens) > max_tokens and len(char_chunk) > 100:
                # Reduce chunk size by 20%
                char_chunk = char_chunk[:int(len(char_chunk) * 0.8)]
                tokens = self.tokenizer(char_chunk, add_special_tokens=False, return_tensors=None)['input_ids']
            
            # Only add non-empty chunks
            if char_chunk.strip():
                chunks.append(char_chunk.strip())
            
            # If we've reached the end, break
            if start + len(char_chunk) >= len(text):
                break
                
            # Move start position with overlap
            start = start + len(char_chunk) - stride_chars
            
        return chunks

    def get_names(self, text):
        names = set()
        for chunk in self._chunk_text(text):
            entities = self.pipeline(chunk)
            names.update({entity['word'] for entity in entities if entity['entity_group'] == 'PER'})
        return list(names)

    def get_entities(self, text):
        entity_set = set()
        for chunk in self._chunk_text(text):
            entities = self.pipeline(chunk)
            for ent in entities:
                entity_set.add(ent['word'])
        return entity_set


if __name__ == "__main__":
    ner_pipe = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

    sample_text = (
        "Sixteen years had Miss Taylor been in Mr. Woodhouse’s family, less as a "
        "governess than a friend, very fond of both daughters, but particularly "
        "of Emma. Between _them_ it was more the intimacy of sisters. Even "
        "before Miss Taylor had ceased to hold the nominal office of governess, "
        "the mildness of her temper had hardly allowed her to impose any "
        "restraint; and the shadow of authority being now long passed away, they "
        "had been living together as friend and friend very mutually attached, "
        "and Emma doing just what she liked; highly esteeming Miss Taylor’s "
        "judgment, but directed chiefly by her own."
    )
    ner_model = NERModel()
    print(ner_model.get_entities(sample_text))
