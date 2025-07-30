# availablemodel s
from dotenv import dotenv_values
import random
import os
'''
model list

gemini-2.5-pro
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-2.0-flash
gemini-2.0-flash-lite

gemini-2.5-flash-lite-preview-06-17
gemini-live-2.5-flash-preview

'''

class Model_Utility_Class:
    # static class for setups, what models to use for what etc
    # Embedding model
    #RAG_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

    # Get project root dynamically to find .env file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    env_file_path = os.path.join(project_root, '.env')
    
    env_vars = dotenv_values(env_file_path)
    api_keys = []
    for key in env_vars:
        if env_vars[key]:  # Only add non-empty values
            api_keys.append(env_vars[key])

    key_dic = {}

    @staticmethod
    def get_next_key(model):
        # Takes the name of the model for use
        # Cycles through a dic
        if not Model_Utility_Class.api_keys:
            raise ValueError(f"No API keys found in .env file at {Model_Utility_Class.env_file_path}. Please add your API keys to the .env file.")
        
        if model not in Model_Utility_Class.key_dic:
            Model_Utility_Class.key_dic[model] = random.randint(0,len(Model_Utility_Class.api_keys)-1)
            return Model_Utility_Class.api_keys[Model_Utility_Class.key_dic[model]]
        else:
            Model_Utility_Class.key_dic[model] +=1
            # reset if its over
            if Model_Utility_Class.key_dic[model] == len(Model_Utility_Class.api_keys): 
                Model_Utility_Class.key_dic[model] = 0
            return Model_Utility_Class.api_keys[Model_Utility_Class.key_dic[model]]
    
    # For embedding
    RAG_EMBEDDING_MODEL = "models/embedding-001"

    # For quering the termbase on terms
    RAG_RETRIEVER_MODEL = "gemini-2.5-flash-lite-preview-06-17"

    # For finding what terms to enter termbase
    GEMINI_NER_MODEL = "gemini-2.5-pro"

    # For translation
    GEMINI_TRANSLATION_MODEL = "gemini-2.5-pro"

    # For back checking, implement later...