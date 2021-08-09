# -*- coding: utf-8 -*-

# General functions used across the project

import os

def getFiles(folder, fileEnd=''):
    # Get a list of files in a specified folder
    fileList = [f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))]
    
    if fileEnd != '':
        fileList = [f for f in fileList
                    if f.lower().endswith((fileEnd))]
        
    return fileList

def getFolders(folder):
    # Get a list of folders in a specified folder
    folderList = [f for f in os.listdir(folder)
                  if os.path.isdir(os.path.join(folder, f))]
    
    return folderList