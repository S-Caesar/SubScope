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
import os

# Take the list of files, remove any that have been analysed already, then write the analysis files for the rest
def parseFiles(folder, fnames, allFiles):
    # Create the output file names to store the parsed data under
    fnamesFull = []
    i = 0
    # TODO: test other file types (e.g. .txt files are probably fine)
    # TODO: if the input is longer than 'x' lines, split it into multiple elements/files to avoid risk of losing progress in a crash/error
    for x in range(len(fnames)):
        if fnames[x].endswith('.srt'):
            fileExtension = '.srt'
        elif fnames[x].endswith('.ass'):
            fileExtension = '.ass'
        
        # Create a list of output files that will be created by this analysis - these will be used later to check whether a file has already been analysed
        # This section uses i for fnamesFull instead of x, as skipped files will still increment x
        fnamesFull.append(fnames[x])
        fnamesFull[i] = fnamesFull[i].replace(fileExtension, '_full.txt')       
        i+=1
    
    # Read each of the files, and compile the contents into a single list, where each element is all the lines for a single episode
    filesSRT = {}
    parseInput = {}
    for x in range(len(fnames)):
        filepath = folder + '/' + fnames[x] # add the file name to the end of the path
        file_contents = open(filepath, 'r', encoding="utf8").read()
        filesSRT[x] = file_contents # compile all the text into one list
        parseInput[x] = filesSRT[x].split('\n') # split each line into a separate element
    parseInput = list(parseInput.values()) # turn the dictionary into a list
    
    # Check whether any of the files have already been analysed, and remove them from the list if the output files exist
    for x in range(len(parseInput)):
        if fnamesFull[x] in allFiles:
            print('File Skipped. Analysis Files Already Exist: ', fnames[x])
            parseInput[x] = ''
            fnamesFull[x] = ''
    parseInput = [x for x in parseInput if x != ''] # remove the entry from the parse input
    fnamesFull = [x for x in fnamesFull if x != ''] # remove the file name from the file list (otherwise it'll be written to as a file name because it just goes through files in order)
    
    # Parse the input, one file (a single line in the list) at a time
    fullTable = pd.DataFrame()
    for x in range(len(parseInput)):
        fullTable = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj']) # prepare the output table
        parseInput[x] = prepParseInput(parseInput[x]) # remove any blacklisted characters, or indications of who is speaking
        
        i=0
        for y in range(len(parseInput[x])):
            if i >= 20:
                print('Rows Complete:', y, '/', len(parseInput[x])) # Print an update to the console to show parsing progress
                i = 0
            i+=1
            
            # Send each element for parsing, then append onto the main table
            jsonOutput = ichiranParse(parseInput[x][y])
            
            # Disable and Enable the 'chained assignment' warning for this sections - it's a false positive
            pd.set_option('mode.chained_assignment', None)
            fullTable = fullTable.append(flattenIchiran(jsonOutput), ignore_index=True)
            pd.reset_option("mode.chained_assignment")
            
        # Check if there's a 'conj' (or 'compound' / 'components') column, and remove it if there is (unlikly to not exist, but can occur in rare cases where just particles are parsed)
        if 'conj' in fullTable:
            del fullTable['conj']
        
        if 'compound' in fullTable:
            del fullTable['compound']
            
        if 'components' in fullTable:
            del fullTable['components']
        
        # Write the output tables for each file to a text file with the same name
        fullTable.to_csv(r'' + folder + '/' + fnamesFull[x], index=None, sep='\t', mode='w')
    
        print('Files Complete:', x+1, '/', len(parseInput))
    print('All Files Analysed. Batch Complete!')
    
    return fullTable


# Takes a list of strings and removes any blacklisted characters, or indications of speaker, from each string, then returns the list of strings
def prepParseInput(parseInput):
    ''''''
    blacklist = '!?.\\/-(),<>[]:;"~ ' + \
                '！？。…．･（）、，＜＞《》〈〉「」『』：；”““”〝〞～♪〝％→・－　' + \
                '\u3000' + '\ufeff1'\
                '０１２３４５６７８９' + '0123456789' + \
                'ＡＢＣＤＥＦＧＨＩＪＫＬⅯＮＯＰＱＲＳＴＵＶＷＸＹＺ' + \
                'ＡＢＭ' \
                'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                'ａｈｒｌ' + \
                ' 　　　　　　　' # weird space thing found in a Toradora sub file; only cleared if I took the whole block of spaces...
    
    for x in range(len(parseInput)):  
        parseInput[x] = re.sub(r'（.+?）', '', parseInput[x]) # remove anything in the line that has brackets either side - these are usually character names
        parseInput[x] = re.sub(r'\(.+?\)', '', parseInput[x]) # repeated with English brackets to catch any differences in formatting (note: brackets have to be escaped here)
        
        for y in range(len(parseInput[x])): 
            if parseInput[x][y] in blacklist:
                parseInput[x] = parseInput[x].replace(parseInput[x][y], ' ')
                
        parseInput[x] = parseInput[x].replace(' ','')
    
    parseInput = [x for x in parseInput if x != ''] # delete the rows that are blank: https://stackoverflow.com/questions/1798796/python-list-index-out-of-range-error-while-iteratively-popping-elements

    return parseInput


# Sends a string to the command prompt for passing with ichiran-cli and returns a json file
def ichiranParse(parseInput):
    print(parseInput)
    loc = 'C:/Users/Steph/quicklisp/local-projects/ichiran' # path to the location of Ichiran
    
    # Note: if there are gaps, or full stops in the console input, then the json will split into additional nested levels
    consoleOutput = subprocess.check_output('ichiran-cli -f ' + parseInput, shell=True, cwd=loc) # run ichiran through the console, and return the parsed json
    jsonOutput = json.loads(consoleOutput) # full json output in list format
    
    return jsonOutput


def flattenIchiran(jsonOutput):
    mainJson = jsonOutput[0][0][0] # main list where each element is [word, information]
    compData = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'conj'])
    # First, check if there are any words with multiple versions, and update the entry to only deal with the first one
    for x in range(len(mainJson)):    
        # The parsed content has multiple readings. Just take all of the data for the first reading, and use this as if it was a normal word        
        if len(mainJson[x]) == 1:
            mainJson[x][1] = mainJson[x][1]['alternative'][0]   
            
        # The parsed content might be a compound word. Need to flatten the first level, then check for a 'compound' column
        elif len(mainJson[x][1]) == 6:
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

'----------------------------------------------------------------------------'

folder = 'C:/Users/Steph/OneDrive/App/Subtitles/Toradora Subs' # will work with OneDrive, but best if folder is set to 'Always Keep On This Device'
file_list = os.listdir(folder)
fnames = [f for f in file_list
          if os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.srt'))
          or os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.ass'))]

allFiles = [f for f in file_list] # get the names of all files in the folder to see if the analysis has already been completed

output = parseFiles(folder, fnames, allFiles)