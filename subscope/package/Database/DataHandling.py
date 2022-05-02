# -*- coding: utf-8 -*-

import pandas as pd
import os

from package.general.file_handling import FileHandling as fh
from package.Options import ManageOptions as mo


def databaseWrapper(create=True, rebuild=False, write=False, overwrite=False):
    '''
    Wrapper for all database functions.
    
    create: create a new database file (if one does not already exist) \t
    rebuild: forcibly create a new database file, erasing an existing one \t
    write: update the database with all analysed files in the 'Subtitles' folder \t
    overwrite: overwrite any existing entries in the database
    '''
    
    startPath = os.getcwd().split('\\')
    folder = '/'.join(startPath) + '/user/subtitles'
    file = 'database.txt'
    
    if create == True:
        createDatabase(file, folder, rebuild)
    
    if write == True:
        writeDatabase(file, folder, overwrite)
        

def createDatabase(file, folder, rebuild=False):
    '''
    Create a blank database file if one does not exist, or if rebuilding.
    
    file: database file name ('database.txt') \t
    folder: location for the database file \t
    rebuild: forcibly create a new database file, erasing an existing one
    '''

    if file not in os.listdir(folder) or rebuild == True:
        database = pd.DataFrame(columns=['reading', 'text', 'kana', 'gloss', 'status'])
        database.to_csv(folder + '/' + file, index=None, sep='\t')
        
    return


def writeDatabase(file, folder, overwrite=False):
    '''
    Write all analysed files to the database.
    
    file: database file name ('database.txt') \t
    folder: location for the database file \t
    overwrite: overwrite any existing entries in the database
    '''

    # Get the source folders and update the database with the contents
    sources = fh.getFolders(folder)
    database = pd.read_csv(folder + '/' + file, sep='\t')

    for source in sources:
        sourceDir = folder + '/' + source + '/Text'
        fullFiles = fh.getFiles(sourceDir, fileEnd='_full.txt')
        database = updateDatabase(sourceDir, fullFiles, database, overwrite)
            
    # Sort by reading, and tidy up the formatting before writing the .txt file
    database = database.sort_values(by=['reading']).fillna(0)
    database.iloc[:, 4:] = database.iloc[:, 4:].astype(int)
    database.to_csv(folder + '/' + file, index=None, sep='\t')
    
    return


def updateDatabase(sourceDir, fullFiles, database, overwrite):
    '''
    Append any new unique dict-form words and details to the database \t
    For each file, indicate the frequency of the word in its column \t

    sourceDir: location for the source '_full.txt' file \t
    fullFiles: list of '_full.txt' files with all the parsed words and definitions
    database: dataframe of all words, definitions, and frequency in each source
    overwrite: overwrite any existing entries in the database
    '''
    
    for x in range(len(fullFiles)):   
        # Split the file name up to create the ID for the column
        folderName = sourceDir.split('/')[-2]
        fileName = fullFiles[x].replace('_full.txt','')
        
        number = str(x+1)
        while len(number) < 3:
            number = '0' + number
        
        metaData = folderName + '/' + fileName + '/' + number
        
        if metaData in database and overwrite == True:
            del database[metaData]

        if metaData not in database:            
            # Check for conjugated words, and replace the main columns with the dict form versions 
            # Then just delete the 'dict' columns, as this info is now in the main columns  
            fullTable = pd.read_csv(sourceDir + '/' + fullFiles[x], sep='\t').fillna(0)
            dictTable = fullTable.copy()
            cols = [['reading', 'dict-reading'], ['text', 'dict-text'], ['kana', 'dict-kana']]
            
            for y in range(len(dictTable)):
                if '【' in dictTable[cols[0][1]][y]:
                    for col1, col2 in cols:
                        dictTable.loc[dictTable.index[y], col1] = fullTable[col2][y]   
            
            for col1, col2 in cols:
                del dictTable[col2]
            
            # Group duplicates, and store the count of each word in the metaData column
            uniqueDict = dictTable.groupby(['reading', 'text', 'kana', 'gloss']).size().reset_index()
            uniqueDict = uniqueDict.rename({0: metaData}, axis=1)
            
            # Remove any lines with no 'gloss' data, then append new words
            uniqueDict = uniqueDict[uniqueDict.gloss != '0']
            database = database.append(uniqueDict)
            
            print(x+1, '/', str(int(len(fullFiles))), 'files analysed')
        
    # Aggregate the database (remove duplicates)
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


def readDatabase():
    '''
    Read the database file into a DataFrame
    '''
    
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    databaseFile = sourceFolder + '/database.txt'
    database = pd.read_csv(databaseFile, sep='\t')
    
    return database


if __name__ == '__main__':
    databaseWrapper(write=True, overwrite=True)