# -*- coding: utf-8 -*-

# General functions used across the project

import os

def getFiles(folder, fileType=''):
    # Get a list of files in a specified folder
    fileList = [f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))]
    
    if fileType != '':
        fileList = [f for f in fileList
                    if f.lower().endswith((fileType))]
        
    return fileList