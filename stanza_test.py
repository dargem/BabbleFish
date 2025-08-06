import stanza
import logging
import time

# Configure logger: WARNING only to avoid info spam during processing
logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.WARNING  # suppress info logs during processing
)

def test_lemmatizer(lang="en"):
    print("loading up")
    stanza.download(lang, processors="tokenize,pos,lemma", verbose=False)
    nlp = stanza.Pipeline(lang=lang, processors="tokenize,pos,lemma", use_gpu=False, verbose=False)

    examples = [
        "The children left the school early.",
        "He saw the saw and picked it up.",
        "She is running faster than before.",
        "They have been going to the gym regularly.",
        "Time flies like an arrow; fruit flies like a banana.",
        "The bass was painted on the head of the bass drum.",
        "I read the book that you read yesterday.",
        "We will wind up the meeting before the wind picks up.",
        "The old man the boat.",
        "Buffalo buffalo Buffalo buffalo buffalo buffalo Buffalo buffalo.",
        "Flying planes can be dangerous.",
        "I can't bear to see another bear suffer.",
        "Will Will will the will to Will?",
        "The complex houses married and single soldiers and their families.",
        "She shed tears while watching the shed burn down."
    ]

    total_tokens = 0
    start_time = time.time()

    # Process all sentences, but don't print token info inside loop
    print("starting processing")
    for text in examples:
        doc = nlp(text)
        for sentence in doc.sentences:
            total_tokens += len(sentence.words)

    elapsed = time.time() - start_time
    tokens_per_min = (total_tokens / elapsed) * 60

    print(f"Processed {total_tokens} tokens in {elapsed:.2f} seconds.")
    print(f"Speed: {tokens_per_min:.2f} tokens per minute.")

if __name__ == "__main__":
    test_lemmatizer()
