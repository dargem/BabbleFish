import os

class File_Extractor:
    def __init__(self, directory_path):
        self.txt_files = []
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith(".txt"):
                    self.txt_files.append(os.path.join(directory_path,filename))
        except (FileNotFoundError, PermissionError) as e:
            print(f"Critical error: {e}")

    def get_files(self):
        return self.txt_files
