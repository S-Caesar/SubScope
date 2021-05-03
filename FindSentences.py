# -*- coding: utf-8 -*-

import pandas as pd
import IchiranParse as ip


# Take a word to be learned, find the episodes it occurs in, and return the parsed sentences

folder = 'C:/Users/Steph/OneDrive/App/Japanese App/Subtitles/SteinsGate'

databaseFile = 'database.txt'

# Read in the database file
database = pd.read_csv(folder + '/' + databaseFile, sep='\t')


targetWord = 'いっしょ'

wordLoc = int(database[database['text']==targetWord].index.values)

# Get the file names for episodes that contain the word
validFiles = database[wordLoc:wordLoc+1]
validFiles = validFiles.loc[:, ~(validFiles != 1).any()]

validFiles = list(validFiles)

for x in range(len(validFiles)):
    # TODO account for the different file endings - need to tie in earlier than this
    validFiles[x] = validFiles[x].replace('_full.txt','.srt')
    validFiles[x] = validFiles[x].split('/')
    validFiles[x] = validFiles[x][3]
    
    
wordLoc = []
for x in range(len(validFiles)):
    lines = pd.read_csv(folder + '/' + validFiles[x], sep='\t')
    lines = lines[lines['1'].str.contains(targetWord)]
    lines = lines.reset_index(drop=True)
