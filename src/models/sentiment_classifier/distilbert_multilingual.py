from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class Distilbert_Sentiment:
    def __init__(self):
        model_name = "tabularisai/multilingual-sentiment-analysis"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def predict_sentiment(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}

        predicted_class = torch.argmax(probabilities, dim=-1).item()
        return sentiment_map[predicted_class]

    
    def predict_sentiment_weighted_average(self, texts):
        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # Define sentiment scale for each class index
        sentiment_weights = torch.tensor([-1, -0.5, 0.0, 0.5, 1])  # shape: (5,)
        # Compute weighted average sentiment scores
        weighted_scores = torch.matmul(probabilities, sentiment_weights)
        return weighted_scores.tolist()

    texts = [
        # English
        "I absolutely love the new design of this app!", "The customer service was disappointing.", "The weather is fine, nothing special.",
        # Chinese
        "这家餐厅的菜味道非常棒！", "我对他的回答很失望。", "天气今天一般。",
        # Spanish
        "¡Me encanta cómo quedó la decoración!", "El servicio fue terrible y muy lento.", "El libro estuvo más o menos.",
        # Arabic
        "الخدمة في هذا الفندق رائعة جدًا!", "لم يعجبني الطعام في هذا المطعم.", "كانت الرحلة عادية。",
        # Ukrainian
        "Мені дуже сподобалася ця вистава!", "Обслуговування було жахливим.", "Книга була посередньою。",
        # Hindi
        "यह जगह सच में अद्भुत है!", "यह अनुभव बहुत खराब था।", "फिल्म ठीक-ठाक थी।",
        # Bengali
        "এখানকার পরিবেশ অসাধারণ!", "সেবার মান একেবারেই খারাপ।", "খাবারটা মোটামুটি ছিল।",
        # Portuguese
        "Este livro é fantástico! Eu aprendi muitas coisas novas e inspiradoras.", 
        "Não gostei do produto, veio quebrado.", "O filme foi ok, nada de especial.",
        # Japanese
        "このレストランの料理は本当に美味しいです！", "このホテルのサービスはがっかりしました。", "天気はまあまあです。",
        # Russian
        "Я в восторге от этого нового гаджета!", "Этот сервис оставил у меня только разочарование.", "Встреча была обычной, ничего особенного.",
        # French
        "J'adore ce restaurant, c'est excellent !", "L'attente était trop longue et frustrante.", "Le film était moyen, sans plus.",
        # Turkish
        "Bu otelin manzarasına bayıldım!", "Ürün tam bir hayal kırıklığıydı.", "Konser fena değildi, ortalamaydı.",
        # Italian
        "Adoro questo posto, è fantastico!", "Il servizio clienti è stato pessimo.", "La cena era nella media.",
        # Polish
        "Uwielbiam tę restaurację, jedzenie jest świetne!", "Obsługa klienta była rozczarowująca.", "Pogoda jest w porządku, nic szczególnego.",
        # Tagalog
        "Ang ganda ng lugar na ito, sobrang aliwalas!", "Hindi maganda ang serbisyo nila dito.", "Maayos lang ang palabas, walang espesyal.",
        # Dutch
        "Ik ben echt blij met mijn nieuwe aankoop!", "De klantenservice was echt slecht.", "De presentatie was gewoon oké, niet bijzonder.",
        # Malay
        "Saya suka makanan di sini, sangat sedap!", "Pengalaman ini sangat mengecewakan.", "Hari ini cuacanya biasa sahaja.",
        # Korean
        "이 가게의 케이크는 정말 맛있어요!", "서비스가 너무 별로였어요.", "날씨가 그저 그렇네요.",
        # Swiss German
        "Ich find dä Service i de Beiz mega guet!", "Däs Esä het mir nöd gfalle.", "D Wätter hüt isch so naja."
    ]

if __name__ == "__main__":
    sentiment_analyser = Distilbert_Sentiment()
    for text, sentiment in zip(sentiment_analyser.texts, sentiment_analyser.predict_sentiment_weighted_average(sentiment_analyser.texts)):
        print(f"Text: {text}\nSentiment: {sentiment}\n")