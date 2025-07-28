import os
import json

class File_Manager():
    def __init__(self, directory_path):
        self.DIRECTORY_PATH = directory_path
        # constructs list of files
        file_list=[]
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith(".txt"):
                    file_list.append(os.path.join(directory_path,filename))
        except (FileNotFoundError, PermissionError) as e:
            print(f"Critical error: {e}")
        self.txt_files = sorted(file_list) 
        # change this later, needs sorting by grabbing chapter num, keep note of possible numbers in the name screwing it up
    
    def get_files(self, file_min_inclusive, file_max_exclusive):
        min_index = file_min_inclusive - 1
        max_index = file_max_exclusive -1

        if min_index < 0 or max_index >= len(self.txt_files):
            raise ValueError("Invalid range")
        return self.txt_files[min_index:max_index]

    def build_glossary(self, data):
        new_folder = self.DIRECTORY_PATH.split("/")[-1] # takes folder name
        file_name = "/home/user/FinetunedMTLBot/data/glossary/" + new_folder + ".json"
        try:
            with open(file_name, 'x') as f:
                json.dump(data,f,indent=4)
            print(f"File '{file_name}' created successfully.")
        except FileExistsError:
            print(f"File '{file_name}' already exists. Writing over")
            with open(file_name, 'w') as f:
                json.dump(data,f,indent=4)
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_glossary(self):
        new_folder = self.DIRECTORY_PATH.split("/")[-1] # takes folder name
        file_name = "/home/user/FinetunedMTLBot/data/glossary/" + new_folder + ".json"
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_glossary_entities(self):
        new_folder = self.DIRECTORY_PATH.split("/")[-1] # takes folder name
        file_name = "/home/user/FinetunedMTLBot/data/glossary/" + new_folder + ".json"
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
            entities = []
            for entry in data:
                entities.append(entry["entity"])
            return entities
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
        except Exception as e:
            print(f"An error occurred: {e}")

    def preprocess_text(self, entities, file_paths):
        # reads txts, inserts entities inside
        for file_path in file_paths:
            with open(file_path,"r") as f:
                txt = f.read()