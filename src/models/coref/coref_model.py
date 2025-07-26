# models/coref/coref_model.py
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
# benched for now bad performance

class CorefResolver:
    def __init__(self, model_name="biu-nlp/lingmess-coref"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)

    def resolve_coreference(self, text):
        """
        Returns:
            clusters (list): Coreference token spans. Resolved text reconstruction is manual.
        """
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Simplified example: the model outputs logits you can decode if you have the label map.
        # Real use requires custom post-processing. Placeholder here:
        return "[Coref resolution not implemented – needs span post-processing]", []
