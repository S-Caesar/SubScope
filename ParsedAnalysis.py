# -*- coding: utf-8 -*-

# Analyse the output table from IchiranParse and return stats
# > prepStats (take the full list of words and return stats)
    # > dataframeDifference

import pandas as pd

# from: ExampleListComparison
def dataframeDifference(df1, df2, which=None):
    # Compare two DataFrames and return a DataFrame with the words only in the first df ('left_only'), only in the second df ('right_only'), or in both ('both')
    ''''''
    # 'which' = 'left_only', 'right_only', 'both'
    dfComp = df1.merge(df2, indicator=True, how='outer')
    if which is None:
        dfDiff = dfComp[dfComp['_merge'] != 'both']
    else:
        dfDiff = dfComp[dfComp['_merge'] == which]
    return dfDiff


def prepStats(fullTable, freqCheck, sign, compCheck):
    # Specify the frequency to check against
    # '_full' [fullTable] files have the following columns: 'reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'
    
    '----------------------------------------------------------------------------'
    # Stats Outputs:
        # noWords - Total Number of Words in the Content
        # noUnknown - The Total Number of Unknown Words in the Content
        #
        # noUnique - Number of Unique Words
        # noUniqueUnk - The Number of Unique Unknown Words
        # noUniqueDict - The Number of Unique Words in Dictionary Form
        # noUniqueDictUnk - The Number of Unique Unknown Words in Dictionary Form
        # 
        # noSpecFreq - The Number of Words with the Frequency Specified (e.g. == 1) (based on the uniqueDict table)
        # 
        # comprehension - The total known words divided by the total number of words
        #
        # noInputComp - The Total Number of Words Required to Get Specified Comprehension
        # noInputCompUnk - The Number of Unknown Words Required to Get Specified Comprehension
    '----------------------------------------------------------------------------'

    noWords = len(fullTable) # count the total number of words
    
    unqiueTable = fullTable.groupby(['text']).size().reset_index() # group any dupicate rows, counting the number of occurances
    unqiueTable.rename(columns = {0: 'freq.'}, inplace=True)
    unqiueTable.sort_values(by=['freq.'], ascending=False, inplace=True) # sort by word frequency, in decending order
    unqiueTable = unqiueTable.reset_index(drop=True)
    noUnique = len(unqiueTable) # count the number of unique words
    
    knownTable = pd.read_excel('C:/Users/steph/OneDrive/App/Japanese App/Top2k-2.xlsx')
    unknownTable = dataframeDifference(fullTable, knownTable, 'left_only').reset_index(drop=True)
    unknownTable.drop(columns=['_merge'], inplace=True)
    noUnknown = len(unknownTable)
    
    unknownFreq = dataframeDifference(unqiueTable, knownTable, 'left_only').reset_index(drop=True)
    unknownFreq.drop(columns=['_merge'], inplace=True)
    noUniqueUnk = len(unknownFreq)
    
    dictTable = fullTable.copy(deep=True)
    for x in range(len(fullTable)):
        if '【' in fullTable['dict-reading'][x]:
            # Need to disable and enable the chained assignment warning while update the dictTable
            pd.set_option('mode.chained_assignment', None)
            dictTable['reading'][x] = fullTable['dict-reading'][x]
            dictTable['text'][x] = fullTable['dict-text'][x]
            dictTable['kana'][x] = fullTable['dict-kana'][x]
            pd.reset_option("mode.chained_assignment")
    # These columns are now integrated in the main columns, so just delete them
    del dictTable['dict-reading']
    del dictTable['dict-text']
    del dictTable['dict-kana']
    
    uniqueDict = dictTable.groupby(['text']).size().reset_index()
    uniqueDict.rename(columns = {0: 'freq.'}, inplace=True)
    uniqueDict.sort_values(by=['freq.'], ascending=False, inplace=True)
    uniqueDict = uniqueDict.reset_index(drop=True)
    noUniqueDict = len(uniqueDict)
    
    # Calculate the number of unique words of the specified frequency range
    freqCheckTable = []
    if sign == '==':
        for x in range(len(uniqueDict)):
            if uniqueDict['freq.'][x] == freqCheck:
                freqCheckTable.append(uniqueDict['text'][x])
    if sign == '<=':
        for x in range(len(uniqueDict)):
            if uniqueDict['freq.'][x] <= freqCheck:
                freqCheckTable.append(uniqueDict['text'][x])                
    if sign == '>=':
        for x in range(len(uniqueDict)):
            if uniqueDict['freq.'][x] >= freqCheck:
                freqCheckTable.append(uniqueDict['text'][x])                          
    noSpecFreq = len(freqCheckTable)
    
    unknownDict = dataframeDifference(uniqueDict, knownTable, 'left_only').reset_index(drop=True)
    unknownDict.drop(columns=['_merge'], inplace=True)
    noUniqueDictUnk = len(unknownDict)
    
    comprehension = round(((noWords - noUnknown) / noWords) * 100) # calculate the current comprehension score
    
    # Detemine the number of unique words required to achieve an input comprehension
    noReqComp = round(noWords * compCheck / 100) # calculate the number of words required for input comprehension
    cumTotal = 0
    for x in range(len(unqiueTable)):
        cumTotal += unqiueTable['freq.'][x]
        if cumTotal >= noReqComp:
            noInputComp = x+1 # +1 to account for the index starting at zero
            break
    
    # Determine the number of unknown words required to get upto the specified comprehension
    cumTotal = noWords - noUnknown
    for x in range(len(unknownFreq)):
        cumTotal += unknownFreq['freq.'][x]
        if cumTotal >= noReqComp:
            noInputCompUnk = x+1 # +1 to account for the index starting at zero
            break
    
    stats = {'0 noWords': noWords,
             '1 noUnknown': noUnknown,
             '2 noUnique': noUnique,
             '3 noUniqueUnk': noUniqueUnk,
             '4 noUniqueDict': noUniqueDict,
             '5 noUniqueDictUnk': noUniqueDictUnk,
             '6 noSpecFreq': noSpecFreq,
             '7 Comprehension': comprehension,
             '8 noInputComp': noInputComp,
             '9 noInputCompUnk': noInputCompUnk}

    return stats

# TODO have a list of analysed content, and have the user select the folder - then cycle through the files and analyse
fullTable = pd.read_csv('C:/Users/steph/OneDrive/App/Subtitles/SteinsGate Subs/STEINS;GATE.S01E01.JA_full.txt', sep='\t')
stats = prepStats(fullTable, 1, '==',  70)
    
    
'''
#TODO: when reading in a string in list/dict format, change it to list/dict with this:
import pandas as pd
import ast

a = pd.read_csv('C:/Users/Steph/OneDrive/App/Japanese App/test.txt', sep='\t') # read in the file

b = ast.literal_eval(a['gloss'][8]) # convert an element to a list/dictionary format

print(b[1]['gloss'])
'''