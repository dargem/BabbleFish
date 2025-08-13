from lingua import Language
class CoreferenceResolver():
    '''
    Resolves coreferences if models available
    '''
    # search for a good multilingual one, or have a few specifications, only need zh,ja,kr

    available_models = {
        Language.CHINESE
    }

    @staticmethod
    def model_available(language:Language):
        return True if language in CoreferenceResolver.available_models else False