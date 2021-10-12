# -*- coding: utf-8 -*-

import pandas as pd
import os

from Program.General import FileHandling as fh

def createDatabase(folder, rebuild=False):
     # Create a blank database file if one does not exist
     databaseFile = 'database.txt'
     if databaseFile not in os.listdir(folder) or rebuild == True:
         database = pd.DataFrame(columns=['reading', 'text', 'kana', 'gloss', 'status'])
         database.to_csv(folder + '/' + databaseFile, index=None, sep='\t')
     return


def writeDatabase(folder, overwrite=False):
    # Read in the database file
    databaseFile = 'database.txt'
    database = pd.read_csv(folder + '/' + databaseFile, sep='\t')
    
    sourceFolders = fh.getFolders(folder)
    for source in sourceFolders:
        sourceDir = folder + '/' + source + '/Text'
        
        fnames = fh.getFiles(sourceDir, fileEnd='_full.txt')

        # Update the database with the specified files
        database = updateDatabase(sourceDir, fnames, database, overwrite)
            
    # Write the database DataFrame to a file
    database = database.sort_values(by=['reading'])
    database = database.fillna(0)

    # Tidy up the formatting before writing to .csv
    databaseStr = database.iloc[:, 0:4]
    databaseInt = database.iloc[:, 4:].astype(int)
    database = databaseStr.join(databaseInt)
    
    database.to_csv(folder + '/' + databaseFile, index=None, sep='\t')
    
    return


# For each file, get the unique dict-form words and details and append any new words to the database
# When going through each file, indicate the number of times the word appears in the file in its column
# Currently just produces a .txt file
def updateDatabase(folder, fnames, database, overwrite):
    if len(fnames) > 0:
        for x in range(len(fnames)):   
            # Split the file name up to create the ID for the column
            folderName = folder.split('/')[-2]
            fileName = fnames[x].replace('_full.txt','')
            
            number = str(x+1)
            while len(number) < 3:
                number = '0' + number
            
            metaData = folderName + '/' + fileName + '/' + number
            if metaData not in database or overwrite == True:
                if metaData in database.columns:
                    del database[metaData]

                # If this entry doesn't exist or the overwrite setting is True, add it
                fullTable = pd.read_csv(folder + '/' + fnames[x], sep='\t').fillna(0)
                
                # Check for conjugated words, and replace the main columns with the dict form versions 
                # Then just delete the 'dict' columns, as this info is now in the main columns
                cols = [['reading', 'dict-reading'], ['text', 'dict-text'], ['kana', 'dict-kana']]
                dictTable = fullTable.copy()
                
                for y in range(len(dictTable)):
                    if '【' in dictTable['dict-reading'][y]:
                        for col1, col2 in cols:
                            dictTable.loc[dictTable.index[y], col1] = fullTable[col2][y]   
                            
                del dictTable['dict-reading'], dictTable['dict-text'], dictTable['dict-kana']
                
                # Group duplicates, and store the count of each word in the source column
                uniqueDict = dictTable.groupby(['reading', 'text', 'kana', 'gloss']).size().reset_index()
                uniqueDict = uniqueDict.rename({0: metaData}, axis=1)
                
                # Remove any lines with no 'gloss' data, then append new words
                uniqueDict = uniqueDict[uniqueDict.gloss != '0']
                database = database.append(uniqueDict)
                
                print(x+1, '/', str(int(len(fnames))), 'files analysed')
        
        # Aggregate the database (remove duplicates)
        # From: https://stackoverflow.com/questions/46826773/how-can-i-merge-rows-by-same-value-in-a-column-in-pandas-with-aggregation-func
        aggDict = {}
        cols = database.columns
        for col in cols:
            if cols.get_loc(col) < 5:
                aggDict[col] = 'first'
            else:
                aggDict[col] = 'sum'

        database = database.groupby(database['reading']).aggregate(aggDict).reset_index(drop=True)
        print('All files analysed')
    
    return database



folder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles'

createDatabase(folder, rebuild=False)
writeDatabase(folder, overwrite=False)
