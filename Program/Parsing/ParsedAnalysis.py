# -*- coding: utf-8 -*-

'''
# Analyse the output table from IchiranParse and return stats
# > prepStats (take the full list of words and return stats)
    # > dataframeDifference (compare two DataFrames, and return one with words only appearing in one of the DataFrames, or that only appear in both)
'''

import pandas as pd
from Program.Options import ManageOptions as mo

def dataframeDifference(df1, df2, column=None, dropMerge=False):
    # Compare two DataFrames and return a DataFrame with the words only in the
    # first df ('left_only'), the second df ('right_only'), or in both ('both')
    ''''''
    # 'column' = 'left_only', 'right_only', 'both'
    dfComp = df1.merge(df2, indicator=True, how='outer')
    
    if column == 'left_and_right':
        dfDiff = dfComp[dfComp['_merge'] != 'both']
    elif column in ['left_only', 'right_only', 'both']:
        dfDiff = dfComp[dfComp['_merge'] == column]
    else:
        dfDiff = dfComp
        
    if dropMerge == True:
        dfDiff = dfDiff.reset_index(drop=True)
        del dfDiff['_merge']
    
    return dfDiff


def simpleAnalysis(fullTable):    
    # '_full' [fullTable] files have the following columns: 'reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'

    noWords = len(fullTable)
    
    # Group any dupicate rows, counting the number of occurances
    uniqueTable = fullTable.groupby(['text']).size().reset_index()
    uniqueTable.rename(columns = {0: 'freq.'}, inplace=True)
    # Sort by word frequency, in decending order
    uniqueTable.sort_values(by=['freq.'], ascending=False, inplace=True)
    uniqueTable = uniqueTable.reset_index(drop=True)
    noUnique = len(uniqueTable)
    
    # Read in the database, and filter for known words (status = 1)
    databaseLoc = mo.getSetting('paths', 'Source Folder')
    database = pd.read_csv(databaseLoc + '/database.txt', sep='\t')
    knownTable = database.loc[database['status'] == 1]
    
    # Compare the database and the '_full' file to find unknown words
    unknownTable = dataframeDifference(fullTable, knownTable, 'left_only', True)
    noUnknown = len(unknownTable)
    
    unknownFreq = dataframeDifference(uniqueTable, knownTable, 'left_only', True)
    noUniqueUnk = len(unknownFreq)
    
    # Calculate the current comprehension score
    comprehension = round(((noWords - noUnknown) / noWords) * 100)

    stats = [noWords,       # Total number of words in the file(s)
             noUnknown,     # Total number of unknown words in the file(s)
             comprehension, # Total known words divided by the total words
             noUnique,      # Number of unique words
             noUniqueUnk]   # Number of unqiue unknown words

    return stats