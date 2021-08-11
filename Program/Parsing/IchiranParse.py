# -*- coding: utf-8 -*-
# Take the list of files, remove any that have been analysed already,
# Then write the output files ('_justText', '_full') for the rest

# parseWrapper (wrapper for parsing a file into output files)
# > renameFiles (return list with modified names with '_justText.txt')
# > checkFiles (find and remove any existing '_justText.txt' from the list)
# > stripText (extract the text lines from the file, and write '_justText.txt')

# > renameFiles (return list with modified names with '_full.txt')
# > checkFiles (find and remove any existing '_full.txt' from the list)
# > parseFiles (parse the text in the _justText.txt', and output '_full.txt')
   # > prepParseInput (remove blacklist characters)
   # > ichiranParse (parse each line of a file and store in DataFrame)
   # > flattenIchiran (normalise any elements (excl. gloss) which are lists)


import subprocess
import json
import pandas as pd
import numpy as np
import re
import timeit
import os

from Program.General import FileHandling as fh

# Take the list of files, remove any that have been analysed already,
# Then write the output files ('_justText', '_full') for the rest
def parseWrapper(folder, files):
    # TODO: test other file types (e.g. .txt files are probably fine)
    # TODO: if the input is longer than 'x' lines, split it into multiple 
    #       temp files to avoid risk of losing progress in a crash/error

    # Create a list of '_justText' file names, then remove any that already exist
    justTextFiles = fh.renameFiles(files.copy(), '_justText', '.txt')
    justText = checkFiles(folder + '/Text', files.copy(), justTextFiles)
    
    # Get the text lines from the files, and write to '_justText.txt' files
    stripText(folder, justText, '_justText', '.txt')
    
    # Create a list of '_justText' files
    fullFiles = fh.renameFiles(files.copy(), '_full', '.txt')
    # Check which '_justText' files exist, and remove from the list if they do
    full = checkFiles(folder + '/Text', files.copy(), fullFiles)

    # Parse the text, and write to 'full.txt' files
    parseFiles(folder, full)
    
    return 


def checkFiles(folder, files, targetFiles):
    ''''''
    # Compare a list of files with files in a folder and remove matching file names
    folderFiles = os.listdir(folder)
    for x in range(len(targetFiles)):
        if targetFiles[x] in folderFiles:
            print('File skipped as it already exists: ', targetFiles[x])
            files[x] = ''
            
    files = [x for x in files if x != '']
    
    return files


def stripText(folder, files, append, fileType=''):
    # Read each of the files, strip out spoken lines, then write to '_justText' files
    outFiles = fh.renameFiles(files.copy(), append, fileType)
    for x in range(len(files)):
        filepath = folder + '/' + files[x]
        
        # Need to leave in blank lines, so the 'line no' matches the original file
        parseInput = pd.read_csv(filepath, sep='\n', names=['sentence'], skip_blank_lines=False).fillna('')
        parseInput['sentence'] = prepParseInput(parseInput['sentence'])
        
        parseInput.index.name = 'line no'
        
        parseInput['sentence'].replace('', np.nan, inplace=True)
        parseInput.dropna(subset=['sentence'], inplace=True)
        
        parseInput.to_csv(folder + '/Text/' + outFiles[x], sep='\t')
        
    return


def prepParseInput(parseInput):
    ''''''
    # Take a list of strings and remove non-whitelist characters,
    # Or indications of speaker, then return the list of strings
    
    # Unicode ranges for kanji, hiragana and katakana
    # From: https://unicode-table.com/en/blocks/katakana/)
    # Regex method
    # From: https://stackoverflow.com/questions/2718196/find-all-chinese-text-in-a-string-using-python-and-regex
    whitelist = re.compile(u'[\u4e00-\u9fff \
                              \u3040-\u309F \
                              \u30A0-\u30FF]', re.UNICODE)
    
    for x in range(len(parseInput)):
        # Remove anything in the line that has brackets either side
        # These are usually just to indicate who is speaking
        # This has to be done with both Japanese and English brackets
        # Note: English brackets have to be escaped
        parseInput[x] = re.sub(r'（.+?）', '', parseInput[x])
        parseInput[x] = re.sub(r'\(.+?\)', '', parseInput[x]) 
        
        for y in range(len(parseInput[x])): 
            if not whitelist.search(parseInput[x][y]):
                parseInput[x] = parseInput[x].replace(parseInput[x][y], ' ')
        
        parseInput[x] = parseInput[x].replace(' ','')
    # Leave the blank lines in for now so that when writing to '_justText.txt'
    # The line number will match with the origina subtitle file
    
    return parseInput


def ichiranParse(parseInput):
    ''''''
    # Parse a string with ichiran-cli and return a json format list
    print(parseInput)
    
    # TODO: made this path relative
    # Path to the location of Ichiran
    loc = 'C:/Users/Steph/quicklisp/local-projects/ichiran' 
    
    # Run ichiran through the console, and return the parsed json
    consoleOutput = subprocess.check_output('ichiran-cli -f ' + parseInput, shell=True, cwd=loc) 
    
    # Full json output in list format
    jsonOutput = json.loads(consoleOutput) 
    
    return jsonOutput


def flattenIchiran(jsonOutput):
    # Main list where each element is [word, information]
    mainJson = jsonOutput[0][0][0] 
    
    mainTable = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
    for x in range(len(mainJson)):
        # If the parsed content has multiple readings, just take the first one  
        if 'alternative' in mainJson[x][1]:
            mainJson[x][1] = mainJson[x][1]['alternative'][0]
        
        # If there are multiple components, take 'components' for normalising
        if 'components' in mainJson[x][1]:
            mainJson[x][1] = mainJson[x][1]['components']
            
        mainTable = mainTable.append(pd.json_normalize(mainJson[x][1])).reset_index(drop=True)
    
    outputTable = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj-prop', 'conj-type', 'neg', 'dict-reading', 'dict-text', 'dict-kana'])
    for x in range(len(mainTable)):
        # If 'conj' is an empty list, then it's a normal word, just append it
        if mainTable['conj'][x] == list():
            outputTable = outputTable.append(mainTable[x:x+1]) 
            
        # If there is Nan in the 'conj' column then skip it (probably a name)
        elif mainTable[x:x+1]['conj'].isnull().values.any():
            continue
        
        # Else, there is data for the 'conj' column; extract and reformat
        else:
            # Copy the 'mainTable' row, or Pandas throws 'SettingWithCopyWarning'
            baseData = mainTable[x:x+1].copy()
            
            # Flatten to: 'prop', 'via', 'readok'
            # Or: 'prop', 'reading', 'gloss', 'readok'
            conjData = pd.json_normalize(mainTable['conj'][x]) 
            
            # Flatten to: 'pos', 'type', 'neg' (if conj is negative)
            posData = pd.json_normalize(conjData['prop'][0]) 

            # If conj. is 'via' a previous conj. (e.g. Past form of Potential form),
            # then 'via' must be flattened to get the same data as in posData
            if len(conjData.columns) == 3:
                # Flatten to: 'prop', 'reading', 'gloss', 'readok'
                conjData = pd.json_normalize(conjData['via'][0])
                
                # Flatten to: 'pos', 'type', 'neg' (if conj is negative)
                viaPosData = pd.json_normalize(conjData['prop'][0]) 
                
                # Append the posData conjugation to each element of viaPosData
                posData['pos'][0] = posData['pos'][0] + ' [via] ' + viaPosData['pos'][0]
                posData['type'][0] = posData['type'][0] + ' [via] ' + viaPosData['type'][0]
            
            # Rename the columns to match main DataFrame
            posData = posData.rename(columns={'pos': 'conj-prop', 'type': 'conj-type'}) 
            
            # Get the dictionary form of the word, and create columns to store
            # the same data as for the main word ('reading', 'text', 'kana')
            # Split the 'reading' info for the dict form to get the kanji and kana
            dictSplit = conjData['reading'][0].split(' ') 
            
            # If the word doesn't have kanji, then there will be no kanji
            # /reading to split, and the result is a single element which 
            # will need to fill all three spaces
            if len(dictSplit) == 1:
                dictText = dictSplit[0]
                dictKana = dictSplit[0]
                
            # If the word does have kanji, it will be split into the kanji, 
            # and a reading surrounded by brackets
            else:
                dictText = dictSplit[0]
                dictKana = dictSplit[1].replace('【', '').replace('】', '') 
            
            # Put all the dictionary data into a table
            dictData = pd.DataFrame({'dict-reading': conjData['reading'], 'dict-text': dictText, 'dict-kana': dictKana}) 
            
            # Nest level for 'gloss' depends on whether there was a 'via'
            if len(baseData['conj'][x][0]) == 4:
                baseData['gloss'][x] = baseData['conj'][x][0]['gloss']
            else:
                baseData['gloss'][x] = baseData['conj'][x][0]['via'][0]['gloss']

            # 'conj' column should now be empty, so just get rid of it
            baseData = baseData.drop(columns=['conj'])
            baseData = baseData.reset_index(drop=True) 
            
            outputData = baseData.join(posData).join(dictData)
            outputTable = outputTable.append(outputData)
            
    # Reset the index, as otherwise every entry will be row index 0
    # Then replace all the 'nan' with '0' to avoid any issues later
    outputTable = outputTable.reset_index(drop=True)
    outputTable = outputTable.fillna(0) 

    return outputTable


def parseFiles(folder, files):
    ''''''
    # Read in and parse each of the files in the list
    # Output a file with a table of parsed words, and the glossary info
    
    # For every file, a 'justText file will need to be read in, 
    # and a '_full' file will need to be created
    justText = fh.renameFiles(files.copy(), '_justText', '.txt')
    full = fh.renameFiles(files.copy(), '_full', '.txt')

    for x in range(len(files)):
        # Prepare the output DataFrame
        fullTable = pd.DataFrame(columns=['line', 'reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
        
        # Read in the appropriate '_justText' file for parsing
        parseInput = pd.read_csv(folder + '/Text/' + justText[x], delimiter = "\t")
        del parseInput['line no']
        parseInput.dropna(inplace=True)
        parseInput = parseInput.reset_index()

        i=0
        # Time the processing of each block of 20 and estimate the remaining duration
        startTime = timeit.default_timer()
        
        for y in range(len(parseInput['sentence'])):
            # Print an update to the console to show parsing progress
            if x > 0 and x % 20 == 0:
                passedTime = timeit.default_timer() - startTime
                estTime = round((passedTime / i) * (len(parseInput['sentence'])-i) / 60, 1)
                   
                print('===================================')                         
                print('Rows Complete:', y, '/', len(parseInput['sentence']))
                print('Estimated time remaining:', estTime, 'minutes')
                print('===================================')

            i+=1
            
            # Send each element for parsing, then append onto the main table
            jsonOutput = ichiranParse(parseInput['sentence'][y])
            fullTable = fullTable.append(flattenIchiran(jsonOutput),ignore_index=True)

            # Add the line number for all added words
            # This can be used to locate a sentence in '_justText' files
            fullTable['line'] = fullTable['line'].fillna(parseInput['index'][y])
            
        # Remove 'conj' / 'compound' / 'components' columns if existing
        delColumns = ['conj', 'compound', 'components']
        for item in delColumns:
            if item in fullTable:
                del fullTable[item]
        
        # Write the output tables for each file to a text file with the same name
        fullTable.to_csv(folder + '/Text/' + full[x], index=None, sep='\t', mode='w')
    
        print('Files Complete:', x+1, '/', len(files))
    print('All Files Analysed. Batch Complete!')

    return

'''
'----------------------------------------------------------------------------'
import os

# will work with OneDrive, but best if folder is set to 'Always Keep On This Device'
folder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles/SteinsGate' 
file_list = os.listdir(folder)
files = [f for f in file_list
             if os.path.isfile(os.path.join(folder, f))
             and f.lower().endswith(('.srt'))
             or os.path.isfile(os.path.join(folder, f))
             and f.lower().endswith(('.ass'))]

# get the names of all files in the folder to see if the analysis has already been completed
allFiles = [f for f in file_list] 

parseWrapper(folder, files, allFiles)
'----------------------------------------------------------------------------'
'''