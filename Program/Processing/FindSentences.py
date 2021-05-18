# -*- coding: utf-8 -*-

import pandas as pd
import sys


# Take a word to be learned, find the episodes it occurs in, and return a dataframe
# containing the episode reference, line number, sentence, and timestamp

def findSentences(folder, database, targetWord):    
    try:
        wordLoc = int(database[database['text']==targetWord].index.values)
    except:
        sys.exit('No matching words found')

    # Get the file names for episodes that contain the word
    validFiles = database[wordLoc:wordLoc+1]
    validFiles = validFiles.loc[:, ~(validFiles != 1).any()]
    validFiles = list(validFiles)
    
    # Get the file name (in the database file it is stored as ShowName/SeriesNo/EpisodeNo/FileName)
    for x in range(len(validFiles)):
        # TODO: account for the different file endings - need to tie in earlier than this
        validFiles[x] = validFiles[x].replace('_full.txt','.srt')
        validFiles[x] = validFiles[x].split('/')
        validFiles[x] = validFiles[x][3]

    # Extract details for the sentence location
    wordLoc = pd.DataFrame(columns=['episode', 'line no', 'sentence', 'timestamp'])
    for x in range(len(validFiles)):
        lines = pd.read_csv(folder + '/' + validFiles[x], sep='\t').rename(columns={'1': 'sentence'})
        targetLines = lines[lines['sentence'].str.contains(targetWord)]
        targetLines = targetLines.reset_index()
        targetLines = targetLines.rename(columns={'index': 'line no'})
        targetLines['episode'] = validFiles[x]
        
        # Extract the timestamp for a given sentence
        # Start at the line number of the selected sentence, then work backwards through the lines until a timestamp is found
        timestamps = []
        for y in range(len(targetLines)):
            i = 1
            found = False
            while found == False:
                if '-->' in lines['sentence'][targetLines['line no'][y]-i]:
                    found = True
                else:
                    i+=1
    
            timestamps.append(lines['sentence'][targetLines['line no'][y]-i]) 
            
        targetLines['timestamp'] = timestamps
        wordLoc = wordLoc.append(targetLines).reset_index(drop=True)
        
    for x in range(len(wordLoc)):
        wordLoc['timestamp'][x] = wordLoc['timestamp'][x].replace(',','.')
        wordLoc['timestamp'][x] = wordLoc['timestamp'][x].replace(' ', '')
        wordLoc['timestamp'][x] = wordLoc['timestamp'][x].split('-->')

    return wordLoc

'----------------------------------------------------------------------------'
folder = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Subtitles/SteinsGate'
databaseFile = 'database.txt'

database = pd.read_csv(folder + '/' + databaseFile, sep='\t')

# TODO: at the moment, it finds setences containing the characters, but that isn't necessarily the word (ばか is in ばかり) - need to exclude incorrect matches of words
targetWord = 'バカ'

wordLoc = findSentences(folder, database, targetWord)