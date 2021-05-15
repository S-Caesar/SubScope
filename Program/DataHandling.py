# -*- coding: utf-8 -*-
import pandas as pd
import os

# For each of the files, get the unique, dict-form, words and details and append any new words to the database
# When going through each file, indicate whether the word appears in the file in its column
def updateDatabase(folder, fnames, database, overwrite):
    '''
    folder: location of the files to be added to the database
    fnames: the list of files to be added to the database
    database: the name and extension of the database file
    overwrite: set whether to overwrite existing columns(1), or skip them (0)
    '''
    
    for x in range(len(fnames)):
        fullTable = pd.read_csv(folder + '/' + fnames[x], sep='\t') # read in the file
        fullTable = fullTable.fillna(0)
        
        # Use the 'dict-form' table, then the words can be looked up in the 'dict-text' column of each file to find the conjugated forms in sentences    
        dictTable = fullTable.copy(deep=True)
        for y in range(len(fullTable)):
            if '【' in fullTable['dict-reading'][y]:
                # Need to disable and enable the chained assignment warning while update the dictTable
                pd.set_option('mode.chained_assignment', None)
                dictTable['reading'][y] = fullTable['dict-reading'][y]
                dictTable['text'][y] = fullTable['dict-text'][y]
                dictTable['kana'][y] = fullTable['dict-kana'][y]
                pd.reset_option('mode.chained_assignment')
        # These columns are now integrated in the main columns, so just delete them
        del dictTable['dict-reading']
        del dictTable['dict-text']
        del dictTable['dict-kana']
        
        uniqueDict = dictTable.groupby(['reading', 'text', 'kana', 'gloss']).size().reset_index()
        del uniqueDict[0]
        uniqueDict = uniqueDict.reset_index(drop=True)

        # Split the file neam up to create the ID for the column
        # TODO expand this to have a broader range of file name configurations
        metaData = fnames[x].split('.')
        showName = metaData[0]
        
        metaData = metaData[1]
        seriesNo = metaData[0:3]
        episodeNo = metaData[3:6]
        
        metaData = showName + '/' + seriesNo + '/' + episodeNo + '/' + fnames[x]
        
        if metaData in database and overwrite == 0:
            # If the column for this entry already exists (and the overwrite setting is 0), then move on to the next file
            continue
        else:
            # Append the file name as a blank column at the end of the database (or replace it if overwriting)
            database[metaData] = ''
    
            # Check whether the word is in the database, and add it if it isn't. Then mark that the word appears in the episode
            for y in range(len(uniqueDict)):
                if (database['reading']==uniqueDict['reading'][y]).any() == False:
                    database = database.append(uniqueDict[y:y+1])
                    
                # Not an else/elif as I want it to go through this after adding a word to the database      
                if (database['reading']==uniqueDict['reading'][y]).any() == True:
                    database = database.reset_index(drop=True)
                    wordLoc = database[database['reading']==uniqueDict['reading'][y]].index.values
                    database[metaData][wordLoc] = 1

    return database

# Take a list of known words, and compare it against the database. Set any words for them list to 'known' (1)
def updateKnown(database, knownList):
    # Indicate the status of each word in the database (unknown (0) /known (1))
    knownTable = pd.read_excel(knownList)
    
    for x in range(len(knownTable)):
        if (database['text']==knownTable['text'][x]).any() == True:
            wordLoc = database[database['text']==knownTable['text'][x]].index.values
            database['status'][wordLoc] = 1
            
    return database

# Remove all lines ('lines'), columns ('columns'), or both ('both') from the database
def clearDatabase(database, clearType):
    # Remove all lines from the database (except headings)
    if clearType == 'lines' or clearType == 'both':
        database = database[0:0]
    
    # Remove all file columns from the database (leave the main word data and status columns)
    if clearType == 'columns' or clearType == 'both':
        database = database[['reading', 'text', 'kana', 'gloss', 'status']]

    return database


folder = 'C:/Users/Steph/OneDrive/App/Japanese App/Subtitles/Toradora'
file_list = os.listdir(folder)
fnames = [f for f in file_list
          if os.path.isfile(os.path.join(folder, f))
          and f.lower().endswith(('_full.txt'))]

databaseFile = 'database.txt'
knownList = 'C:/Users/steph/OneDrive/App/Japanese App/Top2k-2.xlsx' # TODO This can be a file selected by the user (e.g. from Anki) to update the database if they've been using other resources


pd.set_option('mode.chained_assignment', None) # Disable the warning, otherwise Pandas complains

# Create a blank database file if one does not exist
# TODO

# Read in the database file
#database = pd.read_csv(folder + '/' + databaseFile, sep='\t')

# Update the database with the specified files
#database = updateDatabase(folder, fnames, database, 0)
#database = database.sort_values(by=['reading'])

# Update the database with which words are known
#database = updateKnown(database, knownList)

# Remove all lines ('lines'), columns ('columns'), or both ('both') from the database
#database = clearDatabase(database, 'both')

# Write the database DataFrame to a file
#database = database.fillna(0)
#database.to_csv(r'' + folder + '/' + databaseFile, index=None, sep='\t', mode='w')

pd.reset_option('mode.chained_assignment') # Re-enable the warning, otherwise Pandas complains



# TODO Add function for searching for a word in the database, and return the episodes containing the word
# TODO Search for the word in the episodes, and return matching sentences
    # This'll probably need to be in the '_full' files, where all of the words are listed in order
    # Using this will mean it won't be necessary to find words and parse sentences a second time (although that might be quicker)
# TODO Check the sentences, and return in order of fewest unknown words

