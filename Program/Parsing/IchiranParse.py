# -*- coding: utf-8 -*-
# Send a phrase to ichiran for parsing, and put the data into a DataFrame for easy reference (incl. the base and conjugated word where relevent)
# > parseFiles (check files for parsing)
   # > prepParseInput (remove blacklist characters)
   # > ichiranParse (parse each line of a file and store in DataFrame)
   # > flattenIchiran (normalise any elements (excl. gloss) which are lists by adding rows/columns)
# > parseFiles (write the output DataFrames to .txt files)

import subprocess
import json
import pandas as pd
import re

# Take the list of files, remove any that have been analysed already,
# Then write the analysis files for the rest
def parseFiles(folder, fnames, allFiles):
    # TODO: test other file types (e.g. .txt files are probably fine)
    # TODO: if the input is longer than 'x' lines, split it into multiple temp files to avoid risk of losing progress in a crash/error

    
    # Parse the input, one file (a single line in the list) at a time
    
    return 

# Take a list of selected files
# Check if the output files already exist, and remove the file from the list if they do
# Send each file to prepParseInput to remove unwanted content
# Write the list to a .txt file for use later


def renameFiles(files, append):
    # Take the selected list of files
    # Then return a list for a given output file name
    for x in range(len(files)):
        fileName = files[x].split('.')
        del fileName[-1]
        fileName = '.'.join(fileName) + append
        files[x] = fileName
    return files


def checkFiles(folder, files, targetFiles, allFiles):
    ''''''
    # For each file, check for the associated output file
    # Then remove it from the list if the output file exists
    for x in range(len(targetFiles)):
        if targetFiles[x] in allFiles:
            print('File skipped as it already exists: ', targetFiles[x])
            files[x] = ''  
    files = [x for x in files if x != ''] # remove any blank rows
            
    return files


def stripText(folder, files, append):
    ''''''
    # Read each of the files, and compile the contents into a single list
    # Each element of the list is just the text lines for a single episode
    parseInput = {}
    for x in range(len(files)):
        filepath = folder + '/' + files[x]
        parseInput[x] = open(filepath, 'r', encoding="utf8").read().split('\n')
    parseInput = list(parseInput.values())
    
    # Remove any blacklisted characters, or indications of who is speaking
    for x in range(len(parseInput)):
        parseInput[x] = prepParseInput(parseInput[x]) 
    
    # Write the parseInput list to a text file for use later
    for x in range(len(files)):
        
        # Create the output file name
        fileName = files[x].split('.')
        del fileName[-1]
        fileName = '.'.join(fileName) + append
        files[x] = fileName
        
        # Write each line to the file
        textfile = open(folder + '/' + files[x],'w')
        textfile.write('line no' + '\t' + 'sentence' + '\n')
        for y in range(len(parseInput[x])):
            textfile.write(str(y) + '\t' + parseInput[x][y] + '\n')

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
    parseInput = [x for x in parseInput if x != '']

    return parseInput


# TODO review

def ichiranParse(parseInput):
    ''''''
    # Send a string to the command prompt for passing with ichiran-cli and returns a json file
    print(parseInput)
    loc = 'C:/Users/Steph/quicklisp/local-projects/ichiran' # path to the location of Ichiran
    
    # Note: if there are gaps, or full stops in the console input, then the json will split into additional nested levels
    consoleOutput = subprocess.check_output('ichiran-cli -f ' + parseInput, shell=True, cwd=loc) # run ichiran through the console, and return the parsed json
    jsonOutput = json.loads(consoleOutput) # full json output in list format
    
    return jsonOutput


# TODO review
def flattenIchiran(jsonOutput):
    mainJson = jsonOutput[0][0][0] # main list where each element is [word, information]
    compData = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'conj'])
    
    # First, check if there are any words with multiple versions, and update the entry to only deal with the first one
    for x in range(len(mainJson)):
        # The parsed content has multiple readings. Just take all of the data for the first reading, and use this as if it was a normal word        
        try:
            mainJson[x][1] = mainJson[x][1]['alternative'][0]
        except:
            continue
            
        # The parsed content might be a compound word. Need to flatten the first level, then check for a 'compound' column
        if len(mainJson[x][1]) == 6:
            baseData = pd.json_normalize(mainJson[x][1]) # flatten to: 'reading', 'text', 'kana', 'score', 'seq', 'conj' OR 'reading', 'text', 'kana', 'score', 'compound', 'components'
            # If there is a compound column, split the words into separate rows
            if 'compound' in baseData:
                compData = compData.append(pd.json_normalize(mainJson[x][1]['components']))
                mainJson[x] = '' # Set the existing row to blank (will be removed when the loop finishes)          
    mainJson = [x for x in mainJson if x != ''] # remove any balnk rows (these have been converted from compounds to single words)

    mainTable = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
    # Flatten all the normal entries (incl. first versions from 'alternative'), then append the split up and flattened compound entries
    for x in range(len(mainJson)):
        mainTable = mainTable.append(pd.json_normalize(mainJson[x][1])) # flatten to: 'reading', 'text', 'kana', 'score', 'seq', 'conj'
    mainTable = mainTable.append(compData).reset_index(drop=True)
    
    outputTable = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj-prop', 'conj-type', 'neg', 'dict-reading', 'dict-text', 'dict-kana'])
    for x in range(len(mainTable)):
        # The parsed content is just a simple word, with no conjugation, or alternative meanings. It can be appended straight onto the main table
        if mainTable['conj'][x] == list(): # If the 'conj' value is an empty list, then it's a normal word
            outputTable = outputTable.append(mainTable[x:x+1]) # just append the row to the output table; no other processing required
            
        # The parsed content is a conjugated word. The conjugation information must be extracted, and the glossary information relocated to the main 'gloss' column
        else: # There is data for the 'conj' column which needs to be normalised first
            baseData = mainTable[x:x+1]
            
            # Check whether there is anything in the 'conj' column. If there isn't, the input is likely a person/place name - just skip it and go to the next value of x
            if baseData['conj'].isnull().values.any():
                continue
            
            conjData = pd.json_normalize(mainTable['conj'][x]) # flatten to: 'prop', 'via', 'readok' OR 'prop', 'reading', 'gloss', 'readok'
            posData = pd.json_normalize(conjData['prop'][0]) # flatten to: 'pos', 'type', 'neg' (if conj is negative)

            # if the conjugation is via a previous conjugation (e.g. Past form of Potential form), then the 'via' component must be flattened to get the same data as in posData
            if len(conjData.columns) == 3:
                viaConjData = pd.json_normalize(conjData['via'][0]) # flatten to: 'prop', 'reading', 'gloss', 'readok'
                viaPosData = pd.json_normalize(viaConjData['prop'][0]) # flatten to: 'pos', 'type', 'neg' (if conj is negative)
                
                # Append the normal posData conjugation data to the individual elements of viaPosData
                posData['pos'][0] = posData['pos'][0] + ' [via] ' + viaPosData['pos'][0]
                posData['type'][0] = posData['type'][0] + ' [via] ' + viaPosData['type'][0]
                
                conjData = viaConjData # to make sure the following section always takes the proper format of: 'prop', 'reading', 'gloss', 'readok'
            
            posData = posData.rename(columns={'pos': 'conj-prop', 'type': 'conj-type'}) # rename columns to match main DataFrame
            
            # Get the dictionary form of the word, and then create columns to store the same data as for the main word ('reading', 'text', 'kana')  
            dictSplit = conjData['reading'][0].split(' ') # split the 'reading' information for the dictionary form to get the kanji and kana
            
            # If the word doesn't have kanji, then there will be no kanji/reading to split, and the result is a single element which will need to fill all three spaces
            if len(dictSplit) == 1:
                dictText = dictSplit[0]
                dictKana = dictSplit[0]
            # If the word does have kanji, it will be split into the kanji, and a reading surrounded by brackets
            else:
                dictText = dictSplit[0] # get the kanji text
                dictKana = dictSplit[1].replace('【', '').replace('】', '') # get the kana reading (with brackets removed)
            
            dictData = pd.DataFrame({'dict-reading': conjData['reading'], 'dict-text': dictText, 'dict-kana': dictKana}) # put all the dictionary data into a table
            
            # If there was a 'via' conjugation, there will be different nesting; there will be 4 columns if it wasn't a 'via' conjugation
            if len(baseData['conj'][x][0]) == 4:
                baseData['gloss'][x] = baseData['conj'][x][0]['gloss']
            # If there was a 'via' conjugation, then an additional nest must be navigated to find the glossary info
            else:
                baseData['gloss'][x] = baseData['conj'][x][0]['via'][0]['gloss']
    
            baseData = baseData.drop(columns=['conj']) # 'conj' column should now be empty, so just get rid of it
            baseData = baseData.reset_index(drop=True) # need to make sure the index is reset so the posData and dictData will join properly
            
            outputData = baseData.join(posData).join(dictData)
            outputTable = outputTable.append(outputData)
    
    outputTable = outputTable.reset_index(drop=True) # reset the index, as otherwise every entry will be row index 0
    outputTable = outputTable.fillna(0) # replace all the 'nan' with '0' to avoid any issues later

    return outputTable  


# TODO finish review (basically done I think)
def parseFile(folder, files):
    ''''''
    # Read in and parse each of the files in the list
    # Output a file with a table of parsed words, and the glossary info
    
    # For every file, a 'justText file will need to be read in, 
    # and a '_full' file will need to be created
    justText = renameFiles(files.copy(), '_justText.txt')
    full = renameFiles(files.copy(), '_full.txt')

    for x in range(len(files)):
        # Prepare the output DataFrame
        fullTable = pd.DataFrame(columns=['line', 'reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
        
        # Read in the appropriate '_justText' file for parsing
        parseInput = pd.read_csv(folder + '/' + justText[x], delimiter = "\t")
        del parseInput['line no']

        i=0
        for y in range(len(parseInput['sentence'])):
            # Print an update to the console to show parsing progress
            if i >= 20:
                print('Rows Complete:', y, '/', len(parseInput['sentence'])) 
                i = 0
            i+=1
            
            # Send each element for parsing, then append onto the main table
            jsonOutput = ichiranParse(parseInput['sentence'][y])
            
            # Disable and Enable the 'chained assignment' warning for this sections - it's a false positive
            # TODO - maybe I should making a copy it and then updating the copy?
            
            
            
            #pd.set_option('mode.chained_assignment', None)
            fullTable = fullTable.append(flattenIchiran(jsonOutput), ignore_index=True)
            #pd.reset_option('mode.chained_assignment')
            
            
            
            # Add the line number for all added words
            # This can be used to track back to the sentence from the word
            fullTable['line'] = fullTable['line'].fillna(y)
            
        # Check for 'conj' / 'compound' / 'components' columns
        # Then remove them if they exist (unlikly to not exist,
        # but can occur in rare cases where just particles are parsed)
        delColumns = ['conj', 'compound', 'components']
        for item in delColumns:
            if item in fullTable:
                del fullTable[item]
        
        # Write the output tables for each file to a text file with the same name
        fullTable.to_csv(r'' + folder + '/' + full[x], index=None, sep='\t', mode='w')
    
        print('Files Complete:', x+1, '/', len(files))
    print('All Files Analysed. Batch Complete!')

    return


import os

folder = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Subtitles/SteinsGate' # will work with OneDrive, but best if folder is set to 'Always Keep On This Device'
file_list = os.listdir(folder)
files = [f for f in file_list
             if os.path.isfile(os.path.join(folder, f))
             and f.lower().endswith(('.srt'))
             or os.path.isfile(os.path.join(folder, f))
             and f.lower().endswith(('.ass'))]

allFiles = [f for f in file_list] # get the names of all files in the folder to see if the analysis has already been completed

# Prepare lists to check which types of output file have already been created
justTextFiles = renameFiles(files.copy(), '_justText.txt')
justText = checkFiles(folder, files.copy(), justTextFiles, allFiles)
stripText(folder, justText, '_justText.txt')

fullFiles = renameFiles(files.copy(), '_full.txt')
full = checkFiles(folder, files.copy(), fullFiles, allFiles)

parseFile(folder, full)
    












'----------------------------------------------------------------------------'
'''
import os

folder = 'C:/Users/Steph/OneDrive/App/Subtitles/SteinsGate Subs' # will work with OneDrive, but best if folder is set to 'Always Keep On This Device'
file_list = os.listdir(folder)
fnames = [f for f in file_list
          if os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.srt'))
          or os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.ass'))]

allFiles = [f for f in file_list] # get the names of all files in the folder to see if the analysis has already been completed

output = parseFiles(folder, fnames, allFiles)'''