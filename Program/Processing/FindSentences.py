# -*- coding: utf-8 -*-

import pandas as pd

from Program.Database import DataHandling as dh
from Program.Options import ManageOptions as mo

# Take a word to be learned, find the episodes it occurs in, and return a dataframe
# containing the episode reference, line number, sentence, and timestamp

def findSentences(targetWord):
    '''
    Search the database to find all occurances of a given word
    
    folder: the folder containing the main source folders (e.g. SteinsGate)
    database:
    '''
    
    database = dh.readDatabase()
    folder = mo.getSetting('paths', 'Source Folder')
    
    # Select the first row that matches the word
    wordRow = database[database['text']==targetWord]
    wordRow = wordRow[:1]
    wordLoc = int(wordRow.index.values)
    
    # Get the file names for episodes that contain the word
    validFiles = database[wordLoc:wordLoc+1]

    # Remove all the non-source columns
    cols = ['reading', 'text', 'kana', 'gloss', 'status']
    for col in cols:
        del validFiles[col]

    validFiles = validFiles.loc[:, ~(validFiles == 0).any()]
    validFiles = list(validFiles)
    
    # Get the file name (in the database file it is stored as ShowName/FileName/EpisodeNo)
    showFolder = []
    for x in range(len(validFiles)):
        validFiles[x] = validFiles[x].split('/')
        showFolder.append(validFiles[x][0])
        validFiles[x] = validFiles[x][1] + '_full.txt'
        
    # Extract details for the sentence location
    wordLoc = pd.DataFrame(columns=['source', 'episode', 'line no', 'sentence', 'timestamp'])
    template = wordLoc.copy()
    for x in range(len(validFiles)):   
        words = pd.read_csv(folder + showFolder[x] + '/Text/' + validFiles[x], sep='\t')
        
        targetLines = template.copy()

        rawLines = words[words['text'].str.contains(targetWord)]['line']
        dictLines = words[words['dict-text'].str.contains(targetWord)]['line']
        
        targetLines['line no'] = rawLines.append(dictLines).reset_index(drop=True)
        targetLines['episode'] = validFiles[x]
        targetLines['source'] = showFolder[x]
        
        # Extract the sentence
        validFiles[x] = validFiles[x].replace('_full', '_justText')
        lines = pd.read_csv(folder + showFolder[x] + '/Text/' + validFiles[x], sep='\t')

        sentences = []
        for y in range(len(targetLines)):
            line = lines[lines['line no'] == targetLines['line no'][y]].reset_index(drop=True)
            sentences.append(line['sentence'][0])
        targetLines['sentence'] = sentences
        
        # TODO: this only covers .srt files - need a more general form of this
        validFiles[x] = validFiles[x].replace('_justText.txt', '.srt')
        
        # Read in the file, find the sentence, then work backwards to find a timestamp
        file = pd.read_csv(folder + showFolder[x] + '/' + validFiles[x],
                           sep='\n',
                           header=None,
                           skip_blank_lines=False).fillna('')
        
        # Extract the timestamp for a given sentence
        # Start at the line number of the selected sentence,
        # then work backwards through the lines until a timestamp is found
        timestamps = []
        for y in range(len(targetLines)):
            i = 1
            while '-->' not in file[0][targetLines['line no'][y]-i]:
                i+=1
            stampLine = int(targetLines['line no'][y]-i)

            # Format the timestamp, then append to the main list
            stamp = file[0][stampLine]
            stamp = stamp.replace('\n','').replace(',','.').replace(' ', '')
            stamp = stamp.split('-->')
            timestamps.append(stamp)

            # From the timestamp, work forwards, and add on any text lines found
            # There will be an extra '\n' at the end, so remove it when writing the line
            line = ''
            stampLine+=1
            while stampLine < len(file[0]) and file[0][stampLine] != '':
                line += file[0][stampLine] + '\n'
                stampLine += 1
            targetLines.loc[targetLines.index[y], 'sentence'] = line[:-1]

        targetLines['timestamp'] = timestamps
        wordLoc = wordLoc.append(targetLines).reset_index(drop=True)   
        
    return wordLoc


if __name__ == '__main__':
    
    # A few different example words for testing
    #targetWord = 'あのね'
    #targetWord = 'いい'
    #targetWord = 'あっという間に'
    #targetWord = 'あの人'
    #targetWord = 'が'
    targetWord = '人数'
    
    wordLoc = findSentences(targetWord)