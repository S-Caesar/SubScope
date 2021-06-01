# -*- coding: utf-8 -*-

import pandas as pd
import os

# For each file, get the unique, dict-form, words and details and append any new words to the database
# When going through each file, indicate whether the word appears in the file in its column
# Currently just produces a .txt file
def updateDatabase(folder, fnames, database, overwrite):
    '''
    folder: location of the files to be added to the database
    fnames: the list of files to be added to the database
    database: the name and extension of the database file
    overwrite: set whether to overwrite existing columns(1), or skip them (0)
    '''
    databaseFile = 'database.txt'
    if len(fnames) > 0:
        print('Number of valid files: ', str(int(len(fnames))))
        for x in range(len(fnames)):   
            # Split the file name up to create the ID for the column
            folderName = folder.split('/')[-1]
            
            # TODO expand this to have a broader range of file name configurations
            metaData = fnames[x].split('.')
            showName = metaData[0]

            metaData = metaData[1]
            seriesNo = metaData[0:3]
            episodeNo = metaData[3:6]
            
            metaData = folderName + '/' + showName + '/' + seriesNo + '/' + episodeNo + '/' + fnames[x]
            
            if metaData in database and overwrite == False:
                # If the column for this entry already exists (and the overwrite setting is False), then move on to the next file
                continue
            else:
                fullTable = pd.read_csv(folder + '/' + fnames[x], sep='\t')
                fullTable = fullTable.fillna(0)
                
                # Use the 'dict-form' table, then the words can be looked up in the
                # 'dict-text' column of each file to find the conjugated forms in sentences    
                dictTable = fullTable.copy()
                for y in range(len(fullTable)):
                    if '【' in fullTable['dict-reading'][y]:
                        dictTable.loc[dictTable.index[y],'reading'] = fullTable['dict-reading'][y]
                        dictTable.loc[dictTable.index[y],'text'] = fullTable['dict-text'][y]
                        dictTable.loc[dictTable.index[y],'kana'] = fullTable['dict-kana'][y]
                        
                # These columns are now integrated in the main columns, so just delete them
                del dictTable['dict-reading']
                del dictTable['dict-text']
                del dictTable['dict-kana']
                
                uniqueDict = dictTable.groupby(['reading', 'text', 'kana', 'gloss']).size().reset_index()
                del uniqueDict[0]
                uniqueDict = uniqueDict.reset_index(drop=True)

                # Indicate that all the new words are found in this episode
                uniqueDict[metaData] = 1
                # Append the new words to the main database
                database = database.append(uniqueDict)
                
                print(x+1, '/', str(int(len(fnames))), 'files completed')

        # Remove word with no 'gloss' data
        database = database[database.gloss !='0']
        database = database.fillna(0)
        
        # Aggregate the database (remove duplicates)   
        aggDict = {}
        cols = database.columns
        for x in range(len(cols)):
            if x < 5:
                aggDict[cols[x]] = 'first'
            else:
                aggDict[cols[x]] = 'sum'
    
        database = database.groupby(database['reading']).aggregate(aggDict).reset_index(drop=True)
        database.to_csv(r'' + folder + '/' + databaseFile, index=None, sep='\t', mode='w')
    
    return database


# Take a list of known words, and compare it against the database. Set any words for them list to 'known' (1)
def updateKnown(database, knownList):
    # Set the status of each word in the database (unknown (0) / known (1))
    knownTable = pd.read_excel(knownList)
    
    for x in range(len(knownTable)):
        if (database['text']==knownTable['text'][x]).any() == True:
            wordLoc = database[database['text']==knownTable['text'][x]].index.values
            database.loc[database.index[wordLoc], 'status'] = 1
    
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


def consolidateDatabase(showFoldersPath, knownList, overwrite=False, create=False):
    '''
    The main wrapper for using the database
    showFoldersPath: path to the folder where each of the content folders are (e.g. 'SteinsGate')
    knownList: path to file containing list of known words
    overwrite: T/F on whether to overwrite columns that already exist in the individual databases
    create: T/F whether to create a database if one does not already exist
    '''
    # Look through each of the subtitle folders, create any missing database
    # files, then combine all database files into a single file in the level
    # above the episode folders
    databaseFile = 'database.txt'
    mainDatabaseFile = 'mainDatabase.txt'
    
    # Check for the main database file and create it if it doesn't exist
    showFolders = os.listdir(showFoldersPath)
    if mainDatabaseFile not in showFolders:
        # Create a blank database file if one does not exist
        mainDatabase = pd.DataFrame(columns=['reading', 'text', 'kana', 'gloss', 'status'])
        mainDatabase.to_csv(r'' + showFoldersPath + '/' + mainDatabaseFile, index=None, sep='\t', mode='w')
    
    # Remove any files (only want folders)
    # TODO: allow user to select which folders to consolidate
    for x in range(len(showFolders)):
        path = showFoldersPath + '/' + showFolders[x]
        if os.path.isdir(path) == False:
            showFolders[x] = ''
    showFolders = [x for x in showFolders if x != '']
    
    mainDataTable = pd.DataFrame()
    for show in showFolders:
        path = showFoldersPath + '/' + show
        files = os.listdir(path)
        
        if databaseFile not in files and create == True:
            # Create a database for the individual show
            # TODO: also need to create the '_justText' files for this to work properly
            writeDatabase(path, overwrite, knownList)

        if databaseFile in files:
            # If there is a database file, consolidate it
            database = path + '/' + databaseFile
            dataTable = pd.read_csv(database, sep='\t')
            
            # TODO: check whether the database already has the columns that
            #       would be added, and skip if it does
            mainDataTable = mainDataTable.append(dataTable)

    # Write the columns of the database to a dictionary. This will be used to
    # take the first occurance of each word, but keep the indication of which
    # episode the words turn up in (by summing the joined rows)
    # From: https://stackoverflow.com/questions/46826773/how-can-i-merge-rows-by-same-value-in-a-column-in-pandas-with-aggregation-func
    aggDict = {}
    cols = mainDataTable.columns
    for x in range(len(cols)):
        if x < 5:
            aggDict[cols[x]] = 'first'
        else:
            aggDict[cols[x]] = 'sum'

    mainDataTable = mainDataTable.groupby(mainDataTable['reading']).aggregate(aggDict).reset_index(drop=True)
    mainDataTable.to_csv(r'' + showFoldersPath + '/' + mainDatabaseFile, index=None, sep='\t', mode='w')
    
    return mainDataTable


def writeDatabase(folder, overwrite, knownList):
    databaseFile = 'database.txt'
    fileList = os.listdir(folder)
    fnames = [f for f in fileList
              if os.path.isfile(os.path.join(folder, f))
              and f.lower().endswith(('_full.txt'))]
    
    if databaseFile not in fileList:
        # Create a blank database file if one does not exist
        database = pd.DataFrame(columns=['reading', 'text', 'kana', 'gloss', 'status'])
        database.to_csv(r'' + folder + '/' + databaseFile, index=None, sep='\t', mode='w')
    else:
        # Read in the database file if one does exist
        database = pd.read_csv(folder + '/' + databaseFile, sep='\t')
    
    # Update the database with the specified files
    database = updateDatabase(folder, fnames, database, overwrite)
    database = database.sort_values(by=['reading'])    
    
    # Update the database with which words are known
    database = updateKnown(database, knownList)
    
    # Write the database DataFrame to a file
    database = database.fillna(0)
    database.to_csv(r'' + folder + '/' + databaseFile, index=None, sep='\t', mode='w')
    
    return database



'----------------------------------------------------------------------------'
# TODO This can be a file selected by the user (e.g. from Anki) to update the database if they've been using other resources
knownList = 'C:/Users/steph/OneDrive/App/Japanese App/User Data/SRS/Known Words/Top2k-2.xlsx' 

showFoldersPath = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Subtitles'
consolidateDatabase(showFoldersPath, knownList, overwrite=False, create=True)

# Remove all lines ('lines'), columns ('columns'), or both ('both') from the database
#database = clearDatabase(database, 'both')
'----------------------------------------------------------------------------'


# TODO: Some comments from Ella on how to database better
# TODO: Look into doing this with a relational database - have a table for the words,
#       a table for the episodes, and have an ID for each word/episode, 
#       then have a third table which matches up theIDs for each of the other two tables
#       This should be more space efficient than using the single table with binary switch method that I'd currently using
#       This is more useful if the database is mostly zeros, as although the rows are repeated, it removes a lot of empty
#       cells in columns
#       This would ideally be just three tables coving all of the data for the program
