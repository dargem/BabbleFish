import transformers
import time

def extract_triplets_typed(text):
    """
    Extract triplets from mREBEL output format.
    Format: __en__ __sv__ subject __vi__ object __tn__ relation
    """
    triplets = []
    text = text.strip()
    
    # Clean the text
    text = text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").replace("tp_XX", "").strip()
    
    # Split by language markers and process each segment
    segments = text.split("__en__")
    
    for segment in segments:
        if not segment.strip():
            continue
            
        # Look for the pattern: __sv__ subject __vi__ object __tn__ relation
        if "__sv__" in segment and "__vi__" in segment and "__tn__" in segment:
            try:
                # Extract subject
                sv_split = segment.split("__sv__", 1)
                if len(sv_split) > 1:
                    remaining = sv_split[1].strip()
                    
                    # Extract subject and find object
                    vi_split = remaining.split("__vi__", 1)
                    if len(vi_split) > 1:
                        subject = vi_split[0].strip()
                        remaining = vi_split[1].strip()
                        
                        # Extract object and find relation
                        tn_split = remaining.split("__tn__", 1)
                        if len(tn_split) > 1:
                            object_ = tn_split[0].strip()
                            relation = tn_split[1].strip()
                            
                            if subject and object_ and relation:
                                triplets.append({
                                    'head': subject,
                                    'head_type': 'ENTITY',  # Default type
                                    'type': relation,
                                    'tail': object_,
                                    'tail_type': 'ENTITY'   # Default type
                                })
            except Exception as e:
                print(f"Error parsing segment: {segment}, Error: {e}")
                continue
    
    return triplets

if __name__=="__main__":
# Load model and tokenizer
    tokenizer = transformers.AutoTokenizer.from_pretrained("Babelscape/mrebel-base", src_lang="en", tgt_lang="en")
    model = transformers.AutoModelForSeq2SeqLM.from_pretrained("Babelscape/mrebel-base")

    # Text to extract triplets from
    start = time.time()
    with open("data/raw/lotm_files/lotm1.txt") as f:
        text = f.read()
    
    # Tokenizer text
    model_inputs = tokenizer(text, max_length=256, padding=True, truncation=True, return_tensors='pt')
    print(model_inputs)

    # Generate
    generated_tokens = model.generate(model_inputs["input_ids"].to(model.device), attention_mask=model_inputs["attention_mask"].to(model.device))

    # Extract text
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)
    time_taken = time.time() - start
    print(time_taken)
    # Extract triplets


    for idx, sentence in enumerate(decoded_preds):
        print(f'Prediction triplets sentence {idx}')
        print(sentence)
        print(extract_triplets_typed(sentence))