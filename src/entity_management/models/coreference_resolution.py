

# option to use LingMess for more accuracy, from fastcoref
class CoreferenceResolver():
    '''
    Used for coreference resolution on text, precise model LingMessCoreF for better accuracy, cost of speed
    Generally don't use lemmatised text, uses pretrained transformers so can just use base
    '''
    def __init__(self, usePrecise):
        self.model = FCoref() if usePrecise else LingMessCoref()

    def resolve_text(self,text):
        preds = self.model.predict(text)
