# -*- coding: utf-8 -*-

import pandas as pd

# Take a word to be learned, find the episodes it occurs in, and return a dataframe
# containing the episode reference, line number, sentence, and timestamp

def findSentences(folder, database, targetWord): 
    # Make sure only one row is selected
    wordRow = database[database['text']==targetWord]
    while len(wordRow) > 1:
        wordRow = wordRow[:-1]
        
    wordLoc = int(wordRow.index.values)
        
    # Get the file names for episodes that contain the word
    validFiles = database[wordLoc:wordLoc+1]
    
    # Remove all the non-source columns
    # TODO: tidy this up
    del validFiles['reading']
    del validFiles['text']
    del validFiles['kana']
    del validFiles['gloss']
    del validFiles['status']

    validFiles = validFiles.loc[:, ~(validFiles == 0.0).any()]
    validFiles = list(validFiles)
    
    # Get the file name (in the database file it is stored as ShowName/FileName/EpisodeNo)
    showFolder = []
    for x in range(len(validFiles)):
        validFiles[x] = validFiles[x].split('/')
        showFolder.append(validFiles[x][0])
        validFiles[x] = validFiles[x][1]
        
    # Extract details for the sentence location
    wordLoc = pd.DataFrame(columns=['source', 'episode', 'line no', 'sentence', 'timestamp'])
    template = wordLoc.copy()
    for x in range(len(validFiles)):
        rawLines = template.copy()
        dictLines = template.copy()        
        targetLines = template.copy()
        
        validFiles[x] = validFiles[x] + '_full.txt'
        words = pd.read_csv(folder + '/' + showFolder[x] + '/Text/' + validFiles[x], sep='\t')

        rawLines['line no'] = words[words['text'].str.contains(targetWord)]['line']
        dictLines['line no'] = words[words['dict-text'].str.contains(targetWord)]['line']
        targetLines['line no'] = rawLines['line no'].append(dictLines['line no']).reset_index(drop=True)
        
        targetLines['episode'] = validFiles[x]
        targetLines['source'] = showFolder[x]
        
        # Extract the sentence
        validFiles[x] = validFiles[x].replace('_full', '_justText')
        lines = pd.read_csv(folder + '/' + showFolder[x] + '/Text/' + validFiles[x], sep='\t')
        
        # TODO: If I don't use 'sentences' as an intermediary, I get a 'SettingWithCopyWarning'
        #       Probably a more proper way to do this
        sentences = []
        for y in range(len(targetLines)):
            sentences.append(lines['sentence'][targetLines['line no'][y]])
        targetLines['sentence'] = sentences
        
        # TODO: this only covers .srt files - need a more general form of this
        validFiles[x] = validFiles[x].replace('_justText.txt', '.srt')
        
        # Read in the file, find the sentence, then work backwards to find a timestamp
        file = open(folder + '/' + showFolder[x] + '/' + validFiles[x], 'r').readlines()

        # Extract the timestamp for a given sentence
        # Start at the line number of the selected sentence,
        # then work backwards through the lines until a timestamp is found
        timestamps = []
        for y in range(len(targetLines)):
            i = 1
            found = False
            while found == False:
                file[int(targetLines['line no'][y]-i)]
                if '-->' in file[int(targetLines['line no'][y]-i)]:
                    found = True
                else:
                    i+=1
                    
            stampLine = int(targetLines['line no'][y]-i)
            
            # From the timestamp, work forwards, and add on any text lines found
            j = 1
            while file[stampLine+j] != '\n':
                if j == 1:
                    # Updating a line in this way avoids the CopyWarning
                    targetLines.loc[targetLines.index[y], 'sentence'] = file[stampLine+j]
                else:
                    targetLines.loc[targetLines.index[y], 'sentence'] = targetLines['sentence'][y] + file[stampLine+j]
                j+=1
            
            # Remove the last character - it's (always?) a carrage return
            targetLines.loc[targetLines.index[y], 'sentence'] = targetLines.loc[targetLines.index[y], 'sentence'][:-1]
            
            # Format the timestamp, then append to the main list
            stamp = file[int(targetLines['line no'][y]-i)]
            stamp = stamp.replace('\n','')
            stamp = stamp.replace(',','.')
            stamp = stamp.replace(' ', '')
            stamp = stamp.split('-->')

            timestamps.append(stamp)
    
        targetLines['timestamp'] = timestamps
        wordLoc = wordLoc.append(targetLines).reset_index(drop=True)   
        
    return wordLoc


'''
'----------------------------------------------------------------------------'
folder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles'
databaseFile = 'mainDatabase.txt'

database = pd.read_csv(folder + '/' + databaseFile, sep='\t')

targetWord = 'あのね'

wordLoc = findSentences(folder, database, targetWord)
'----------------------------------------------------------------------------'
'''