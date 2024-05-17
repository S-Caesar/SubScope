import os


class FileHandling:
    
    @staticmethod
    def get_files(folder, extension=''):
        file_list = []
        if folder:
            # Get a list of files in a specified folder
            file_list = [f for f in os.listdir(folder)
                         if os.path.isfile(os.path.join(folder, f))]

            if extension:
                file_list = [f for f in file_list
                             if f.lower().endswith(extension)]
            
        return file_list
    
    @staticmethod
    def get_folders(folder):
        # Get a list of folders in a specified folder
        folder_list = [f for f in os.listdir(folder)
                       if os.path.isdir(os.path.join(folder, f))]
        
        return folder_list

    def rename_files(self, files, append, extension=""):
        # Add text to the end of a file name. Optionally, change the file extension.
        renamed_files = []
        for file in files:
            renamed_file = self.rename_file(file, append, extension=extension)
            renamed_files.append(renamed_file)
        return renamed_files

    @staticmethod
    def rename_file(file, append, extension=""):
        file_name = file.split(".")
        file_name[-2] = file_name[-2] + append

        if extension != "":
            if "." in extension:
                extension = extension.replace(".", "")
            file_name[-1] = extension
        renamed_file = ".".join(file_name)
        return renamed_file
