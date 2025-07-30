import os
import json

class File_Manager():
    def __init__(self, directory_path):
        self.DIRECTORY_PATH = directory_path
        # Get project root dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        
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
    
    def get_files(self, start_idx, end_idx):
        if start_idx < 0 or end_idx > len(self.txt_files):
            raise ValueError("Invalid range")
        return self.txt_files[start_idx:end_idx]

    def build_glossary(self, data):
        new_folder = self.DIRECTORY_PATH.split("/")[-1] # takes folder name
        file_name = os.path.join(self.project_root, "data", "glossary", f"{new_folder}.json")
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
        file_name = os.path.join(self.project_root, "data", "glossary", f"{new_folder}.json")
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"File '{file_name}' not found")
        except Exception as e:
            print(f"An error occurred: {e}")

    def preprocess_text(self, entities, file_paths):
        # reads txts, inserts entities inside
        for file_path in file_paths:
            with open(file_path,"r") as f:
                txt = f.read()

    def get_entity_chapter_presence(self, entities, start_idx, end_idx):
        file_paths = self.get_files(start_idx, end_idx)
        entity_chapter_presence = {}
        
        # Create empty lists for all entity's
        for entity in entities:
            entity_chapter_presence[entity] = []
        
        for i, file_path in enumerate(file_paths):
            try:
                with open(file_path,'r', encoding="utf-8") as f:
                    txt = f.read()
                    for entity in entities:
                        if entity in txt:
                            entity_chapter_presence[entity].append(start_idx+i)
            except(FileNotFoundError, PermissionError) as e:
                print(f"Critical error: {e}")
        return entity_chapter_presence