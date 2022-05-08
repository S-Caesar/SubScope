# -*- coding: utf-8 -*-

import os

class FileHandling:
    
    @staticmethod
    # TODO: add support for lists of extensions, if multiple file types are required (e.g. .srt, .ass)
    def getFiles(folder, extn=''):
        fileList = []
        if folder != '':
            # Get a list of files in a specified folder
            fileList = [f for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder, f))]

            if extn != '':
                fileList = [f for f in fileList
                            if f.lower().endswith((extn))]
            
        return fileList
    
    @staticmethod
    def getFiles_multi(folder, extns=[]):
        # Get a list of files in a specified folder
        fileList = [f for f in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, f))]
        
        outputList = []
        if extns != []:
            for extn in extns:
                outputList.append([f for f in fileList if f.lower().endswith((extn))])
            
        return outputList
    
    @staticmethod
    def getFolders(folder):
        # Get a list of folders in a specified folder
        folderList = [f for f in os.listdir(folder)
                      if os.path.isdir(os.path.join(folder, f))]
        
        return folderList
    
    @staticmethod
    def renameFiles(files, append, extn=''):
        # Add text to the end of a file name. Optionally, change the file extension.
        if type(files) == str:
            files = [files]

        renamed_files = []
        for file in files:
            file_name = file.split('.')
            file_name[-2] = file_name[-2] + append
            
            if extn != '':
                if '.' in extn:
                    extn = extn.replace('.', '')
                file_name[-1] = extn
            renamed_files.append('.'.join(file_name))
        return renamed_files
