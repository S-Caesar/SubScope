# -*- coding: utf-8 -*-

# General functions used across the project

import os

# TODO: add support for lists of extensions, if multiple file types are required (e.g. .srt, .ass)
def getFiles(folder, fileEnd=''):
    # Get a list of files in a specified folder
    fileList = [f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))]
    
    if fileEnd != '':
        fileList = [f for f in fileList
                    if f.lower().endswith((fileEnd))]
        
    return fileList


def getFiles_multi(folder, extensions=[]):
    # Get a list of files in a specified folder
    fileList = [f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))]
    
    outputList = []
    if extensions != []:
        for item in extensions:
            outputList.append([f for f in fileList if f.lower().endswith((item))])
        
    return outputList


def getFolders(folder):
    # Get a list of folders in a specified folder
    folderList = [f for f in os.listdir(folder)
                  if os.path.isdir(os.path.join(folder, f))]
    
    return folderList


def renameFiles(files, append, fileType=''):
    # Add text to the end of a file name. Optionally, change the file extension.
    if type(files) == str:
        files = [files]
    
    for x in range(len(files)):
        fileName = files[x].split('.')
        fileName[-2] = fileName[-2] + append
        
        if fileType != '':
            if '.' in fileType:
                fileType = fileType.replace('.', '')
            fileName[-1] = fileType

        files[x] = '.'.join(fileName)

    return files