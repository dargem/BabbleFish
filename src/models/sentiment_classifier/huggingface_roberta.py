from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np
from scipy.special import softmax
import csv
import urllib.request


class Roberta_Sentiment:
    def __init__(self):
         # Tasks:
         # emoji, emotion, hate, irony, offensive, sentiment
         # stance/abortion, stance/atheism, stance/climate, stance/feminist, stance/hillary
        task='sentiment'
        MODEL = f"cardiffnlp/twitter-roberta-base-{task}"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.labels = []
        # download label mapping
        mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
        with urllib.request.urlopen(mapping_link) as f:
            html = f.read().decode('utf-8').split("\n")
            csvreader = csv.reader(html, delimiter='\t')
            self.labels = [row[1] for row in csvreader if len(row) > 1]
        # PT
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
        self.model.save_pretrained(MODEL)
    
    def classify_text(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        for i in range(scores.shape[0]):
            l = self.labels[ranking[i]]
            s = scores[ranking[i]]
            print(f"{i+1}) {l} {np.round(float(s), 4)}")