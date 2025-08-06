import spacy
import logging
import time

# Configure logger
logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO
)

def test_lemmatizer(model_name="en_core_web_lg"):
    try:
        nlp = spacy.load(model_name)
    except OSError:
        logging.error(f"Model '{model_name}' not found. Run 'python -m spacy download {model_name}' to install.")
        return

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

    for text in examples:
        doc = nlp(text)
        total_tokens += len(doc)

        #logging.info(f"\nInput: {text}")
        #for token in doc:
            #logging.info(f"{token.text:15} POS: {token.pos_:10} Lemma: {token.lemma_}")

    elapsed = time.time() - start_time
    tokens_per_min = (total_tokens / elapsed) * 60
    logging.info(f"\nProcessed {total_tokens} tokens in {elapsed:.2f} seconds.")
    logging.info(f"Speed: {tokens_per_min:.2f} tokens per minute.")

if __name__ == "__main__":
    test_lemmatizer()
