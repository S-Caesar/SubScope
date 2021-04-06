# Send a phrase to ichiran for parsing, and put the data into a DataFrame for easy reference (incl. the base and conjugated word where relevent)
# > parseFiles (check files for parsing)
   # > prepParseInput (remove blacklist characters)
   # > ichiranParse (parse each line of a file and store in DataFrame)
       # > normaliseData (normalise any elements which are lists by adding rows/columns)
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
    fnamesTrimmed = []
    i = 0
    # TODO: test other file types (e.g. .txt files are probably fine)
    # TODO: if the input is longer than 'x' lines, split it into multiple elements/files to avoid risk of losing progress in a crash/error
    for x in range(len(fnames)):
        if fnames[x].endswith('.srt'):
            fileExtension = '.srt'
        elif fnames[x].endswith('.ass'):
            fileExtension = '.ass'
        
        # Create a list of output files that will be created by this analysis - these will be used later to check whether a file has already been analysed
        # This section uses i for fnamesFull/Trimmed instead of x, as skipped files will still increment x
        fnamesFull.append(fnames[x])
        fnamesFull[i] = fnamesFull[i].replace(fileExtension, '_full.txt')
        
        fnamesTrimmed.append(fnames[x])
        fnamesTrimmed[i] = fnamesTrimmed[i].replace(fileExtension, '_trimmed.txt')
        
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
        if fnamesFull[x] in allFiles or fnamesTrimmed[x] in allFiles:
            print('File Skipped. Analysis Files Already Exist: ', fnames[x])
            parseInput[x] = ''
    parseInput = [x for x in parseInput if x != '']
    
    # Parse the input, one file (a single line in the list) at a time
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
            fullTable = fullTable.append(ichiranParse(parseInput[x][y]), ignore_index=True)
        
        # Write the output tables for each file to a text file with the same name
        fullTable.to_csv(r'' + folder + '/' + fnamesFull[x], index=None, sep=' ', mode='w')
        
        trimmedTable = fullTable.groupby(['reading']).size().reset_index() # group any dupicate rows, counting the number of occurances
        trimmedTable.rename(columns = {0: 'freq.'}, inplace=True)
        trimmedTable.sort_values(by=['freq.'], ascending=False, inplace=True) # sort by word frequency, in decending order
        trimmedTable.to_csv(r'' + folder + '/' + fnamesTrimmed[x], index=None, sep=' ', mode='w')
    
        print('Files Complete:', x+1, '/', len(parseInput))
    print('All Files Analysed. Batch Complete!')
    
    return 


# Takes a list of strings and removes any blacklisted characters, or indications of speaker, from each string, then returns the list of strings
def prepParseInput(parseInput):
    ''''''
    blacklist = '!?.\\/-(),<>[]:;"~ ' + \
                '！？。…．･（）、，＜＞《》「」『』：；”“〞～♪〝％→・　' + \
                '\u3000' + '\ufeff1' + \
                '０１２３４５６７８９' + '0123456789' + \
                'ＡＢＣＤＥＦＧＨＩＪＫＬⅯＮＯＰＱＲＳＴＵＶＷＸＹＺ' + \
                'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for x in range(len(parseInput)):  
        parseInput[x] = re.sub(r'（.+?）', '', parseInput[x]) # remove anything in the line that has brackets either side - these are usually character names
        parseInput[x] = re.sub(r'\(.+?\)', '', parseInput[x]) # repeated with English brackets to catch any differences in formatting (note: brackets have to be escaped here)
        
        for y in range(len(parseInput[x])): 
            if parseInput[x][y] in blacklist:
                parseInput[x] = parseInput[x].replace(parseInput[x][y], ' ')
                
        parseInput[x] = parseInput[x].replace(' ','')
    
    parseInput = [x for x in parseInput if x != ''] # delete the rows that are blank: https://stackoverflow.com/questions/1798796/python-list-index-out-of-range-error-while-iteratively-popping-elements

    return parseInput


# Sends a string to the command prompt for passing with ichiran-cli, and returns a DataFrame with each of the component words, plus their definitions
def ichiranParse(parseInput):
    ''''''
    loc = 'C:/Users/Steph/quicklisp/local-projects/ichiran' # path to the location of Ichiran
    
    # Note: if there are gaps, or full stops in the console input, then the json will split into additional nested levels
    consoleOutput = subprocess.check_output('ichiran-cli -f ' + parseInput, shell=True, cwd=loc) # run ichiran through the console, and return the parsed json
    jsonOutput = json.loads(consoleOutput) # full json output in list format
    mainJson = jsonOutput[0][0][0] # main list where each element is [word, information]
    
    allHeadings = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj', 'suffix', 'alternative', 'compound', 'components'])
    fullTable = pd.DataFrame(mainJson, columns=['word','info','other'])
    fullTable = allHeadings.append(pd.DataFrame.from_dict(pd.json_normalize(fullTable['info'])))
    
    # TODO: check if there are any major issues with just taking the first version of a word
    fullTable = normaliseData(fullTable, ['alternative'], 0, 'first') # since this is different versions of a word, just take the first one
    fullTable = normaliseData(fullTable, ['compound', 'components'], 1, 'all') # since this is breaking down a compound word, take all of the elements
    
    fullTable = fullTable.drop(columns=['alternative', 'compound', 'components']) # remove uneeded columns
    fullTable = fullTable.dropna(subset=['conj']) # remove any 'conj' columns that contain nan, as this will be duplicate data (e.g. due to 'components'), or invalid rows
    
    fullTable = fullTable.fillna(0) # get rid of any remaining nan, as they are bound to cause issues otherwise...
    
    return fullTable


# Takes a DataFrame containing lists as an element, and flattens these elements into new rows/columns in the DataFrame, which is then returned
def normaliseData(mainTable, targetColumns, normColumn, request):
    '''''' 
    subTable = pd.DataFrame(mainTable, columns=targetColumns) # create a new table with target data as the columns
    subTable = subTable.dropna().reset_index(drop=True) # get rid of anything that doesn't have a value for the target data
    
    subFull = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
    for x in range(len(subTable)):
        if request == 'all':
            subFull = subFull.append(pd.json_normalize(subTable[targetColumns[normColumn]][x])) # return all list elements as new rows (e.g. in the case of breaking up compound words)
        elif request == 'first':
            subFull = subFull.append(pd.json_normalize(subTable[targetColumns[normColumn]][x][0])) # only return the first list element as a new row (e.g. in the case of 'alternative' versions of words)
    mainTable = mainTable.append(subFull).reset_index(drop=True)
    
    return mainTable

'----------------------------------------------------------------------------'

folder = 'C:/Users/Steph/Desktop/App/Subtitles/SteinsGate Subs'
file_list = os.listdir(folder)
fnames = [f for f in file_list
          if os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.srt'))
          or os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('.ass'))]

allFiles = [f for f in file_list] # get the names of all files in the folder to see if the analysis has already been completed

output = parseFiles(folder, fnames, allFiles)