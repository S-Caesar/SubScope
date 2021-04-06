# from ReadParseWriteOrder

import pandas as pd
from sudachipy import tokenizer, dictionary
from collections import Counter
import re

'____________________________________________________________________________'

blacklist = '!' + '?' + '？' + '！' + '…' + ' ' + '(' + ')' + '」' + '「' + \
            '～' + '-' + '>' + '･' + '♪' + '”' + '“' + '--' + '〞' + ',' + \
            '〞' + '〝' + '％' + '。' + '｡' + '→' + '＜' + '＞' + '[' + ']' \
            '\\\\' + '---' + ':' + '：' + '.' + '，' + '、' + '・' + '『' + '』' + \
            '------' + '》' + '《' + '\u3000' + '\ufeff' + \
            \
            '０' + '１' + '２' + '３' + '４' + '５' + '６' + '' + '８' + '' + \
            '0' + '1' + '2' + '3' + '4' + '5' + '6'+ '7' + '8' + '9' + \
            \
            '' + '' + 'Ｃ' + 'Ｄ' + '' + 'Ｆ' + 'Ｇ' + '' + 'Ｉ' + '' + 'Ｋ' + \
            'Ｌ' + '' + '' + 'Ｏ' + 'Ｐ' + '' + '' + 'Ｓ' + '' + '' + 'Ｕ' + '' + \
            '' + 'Ｘ' + '' + '' + \
            \
            'A' + 'B' + 'C'
            # TODO take out the particles from the frequency lists
'____________________________________________________________________________'

def trimExcess(inputList, fileType): # check all lines in the file and remove any unnecessary lines
    '''''' # shows the inputs when using the fuction
    if fileType == 'srt':
        inputList = [x for x in inputList if x not in blacklist] # TODO have a look at regex # Note, some of the blacklist punctuation is English and some is Japanese
        for x in range(len(inputList)): 
            if type(inputList[x]) == int or '0' in inputList[x]: 
                inputList[x] = 0 # if I delete a row here it causes an error because the length of the list has changed - there's probably an elegant way around it, but this'll do for now
            else:
                inputList[x] = re.sub('（.*?）', '', inputList[x]) # bracketed sections usually just inidcate a speaker, so take this bit out - from: https://stackoverflow.com/questions/8784396/how-to-delete-the-words-between-two-delimiters
            
        for x in range(len(inputList)):
            try:
                float(inputList[x])
                inputList[x] = 0
            except ValueError:
                continue
    
        inputList = [x for x in inputList if x != ''] # delete the rows that are blank
        inputList = [x for x in inputList if x != 0] # delete the rows that are 0: https://stackoverflow.com/questions/1798796/python-list-index-out-of-range-error-while-iteratively-popping-elements
        
    elif fileType == 'ass':
        tempList = []
        for x in range(len(inputList)):
            if 'Dialogue' in inputList[x]:
                splitLine = inputList[x].split(',')
                tempList.append(splitLine[-1])
            else:
                continue
        inputList = tempList
        
        for x in range(len(inputList)):
            inputList[x] = re.sub('（.*?）', '', inputList[x])
            if 'www' in inputList[x] or 'N' in inputList[x]: # TODO workaround for the Shirokuma Cafe subs, where there is authoriship info at the end
                inputList[x] = ''
        
        inputList = [x for x in inputList if x not in blacklist]
        inputList = [x for x in inputList if x != '']
        inputList = [x for x in inputList if x != 0]

    return inputList

'----------------------------------------------------------------------------'
# from: ExampleListComparison
def dataframe_difference(df1, df2, which=None):
    ''''''
    # 'which' = 'left_only', 'right_only', 'both'
    comparison_df = df1.merge(df2, indicator=True, how='outer')
    if which is None:
        diff_df = comparison_df[comparison_df['_merge'] != 'both']
    else:
        diff_df = comparison_df[comparison_df['_merge'] == which]
    return diff_df

'----------------------------------------------------------------------------'
# read the subtitle files and parse the text
def prepWords(folder, fnames, knownWordsList):
    ''''''
    filesSRT = {}
    filesASS = {}
    for file in fnames:
        if file.endswith('.srt'):
            filepath = folder + '/' + file # add the file name to the end of the path
            file_contents = open(filepath, 'r', encoding="utf8").read()
            filesSRT[file] = file_contents # compile all the text into one list
        elif file.endswith('.ass'):
            filepath = folder + '/' + file
            file_contents = open(filepath, 'r', encoding="utf8").read()
            filesASS[file] = file_contents

    mylistSRT = list(filesSRT.values())
    mylistSRT = [word for line in mylistSRT for word in line.split()] # from: https://stackoverflow.com/questions/44085616/how-to-split-strings-inside-a-list-by-whitespace-characters
    mylistSRT = trimExcess(mylistSRT, 'srt') # remove all the unnecessary information
    
    mylistASS = list(filesASS.values())
    mylistASS = [word for line in mylistASS for word in line.split('\n')]
    mylistASS = trimExcess(mylistASS, 'ass')
    
    mylist = mylistSRT + mylistASS

    # From: ExampleParseTranslate
    tokenizer_obj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.C # SplitMode can be A, B or C, with decreasing granularity
    
    # Turn the 'Morpheme' object into a standard list, and put all of them in one list
    allSplitWords = []
    for x in range(len(mylist)):
        splitWords = tokenizer_obj.tokenize(mylist[x], mode)
        i = 0
        while i < len(splitWords):
            if str(splitWords[i]) == '（' or str(splitWords[i]) == '）': # TODO probably a better way to do this, but not sure at the moment
                i+=1 # skip the line if it is a bracket
            else:
                allSplitWords.append(str(splitWords[i]))
                i+=1
    
    allSplitWords = trimExcess(allSplitWords, 'srt')
    wordFrequency = Counter(allSplitWords) # count the number of occurances of each word: https://stackoverflow.com/questions/2600191/how-can-i-count-the-occurrences-of-a-list-item
    
    # get the component parts of the Counter, then put them in a DataFrame, and sort by frequency
    words = list(wordFrequency.keys())
    freq = list(wordFrequency.values())
    wordFreq = pd.DataFrame({'All Words':words, 'AW Freq':freq}) # turn the list into a Pandas DataFrame for writing to Excel
    wordFreqSort = wordFreq.sort_values(by=['AW Freq'], ascending=False) # sort list based on the frequency
    wordFreqSort['Cum Total'] = wordFreqSort['AW Freq'].cumsum() # log the cumulative total for each line
    wordFreqSort.reset_index(drop=True, inplace=True) # to make sure the column can be combined with the known words columns in place - from: https://stackoverflow.com/questions/32801806/pandas-concat-ignore-index-doesnt-work

    # read in the known words list, and compare it with the list of words in the subtitle file
    if knownWordsList != '':
        knownWords = pd.read_excel(knownWordsList) # read in the known words
        unknownWords = dataframe_difference(wordFreq, knownWords, which='left_only') # note that both DataFrames need to have the same name for the merging columns, else this returns an error
        unknownWordsSort = unknownWords.sort_values(by=['AW Freq'], ascending=False)
        del unknownWordsSort['_merge'] # delete the merge column
        unknownWordsSort.columns = ['Unknown', 'Unk Freq']
        unknownWordsSort['Cum Unknown'] = unknownWordsSort['Unk Freq'].cumsum() # log the cumulative total for each line
        unknownWordsSort.reset_index(drop=True, inplace=True) # to make sure the column can be combined with the all words columns in place
    else:
        unknownWordsSort = pd.DataFrame()
        #unknownWordsSort.columns = ['Unknown', 'Unk Freq']
    
    output = pd.concat([wordFreqSort, unknownWordsSort], axis=1)

    return output

'----------------------------------------------------------------------------'
def countWords(sign, dfInput, wordColumn, freqColumn, numberOccurances):
    ''''''
    dfOutput = []
    if sign == '<=':
        for x in range(len(dfInput[freqColumn])):
            if dfInput[freqColumn][x] <= numberOccurances:
                dfOutput.append(dfInput[wordColumn][x])
    elif sign == '>=':
        for x in range(len(dfInput[freqColumn])):
            if dfInput[freqColumn][x] >= numberOccurances:
                dfOutput.append(dfInput[wordColumn][x])
    elif sign == '==':
        for x in range(len(dfInput[freqColumn])):
            if dfInput[freqColumn][x] == numberOccurances:
                dfOutput.append(dfInput[wordColumn][x])
    return len(dfOutput)

'----------------------------------------------------------------------------'
def subStats(inputDataFrame, allWords, allFreq, unknownWords, unknownFreq, sign, numberOccurnaces, inputComp):
    ''''''
    inputMaths = inputDataFrame.fillna(0) # create a maths version of the input DataFrame for use with count()
    noUnqiueWords = countWords('>=', inputDataFrame, allWords, allFreq, 0) # count the number of unique words
    singleWords = countWords('==', inputDataFrame, allWords, allFreq, 1) # count the number of words that only appear once
    xOccurance = countWords(sign, inputDataFrame, allWords, allFreq, numberOccurnaces) # count the number of words that appear a specified number of times
    totalWords = sum(inputMaths[allFreq]) # count the total number of words
    totalUnknown = int(sum(inputMaths[unknownFreq])) # count the total number of unknown words
    
    comprehension = 0
    if totalWords != totalUnknown:
        comprehension = round(((totalWords - totalUnknown) / totalWords) * 100) # calculate the current comprehension score
    
    wordsSetComp = 0
    reqWords = round(totalWords * inputComp / 100) # calculate the number of words required for input comprehension
    for x in range(len(inputMaths['Cum Total'])):
        if inputMaths['Cum Total'][x] >= reqWords:
            wordsSetComp = x+1 # +1 to account for the index starting at zero
            break
    
    unknownSetComp = 0
    reqUnkWords = round(totalWords * inputComp / 100) - totalUnknown
    for x in range(len(inputMaths['Cum Unknown'])):
        if inputMaths['Cum Unknown'][x] >= reqUnkWords:
            unknownSetComp = x+1
            break
        
    stats = pd.DataFrame([noUnqiueWords,
                          singleWords,
                          xOccurance,
                          totalWords,
                          totalUnknown,
                          comprehension,
                          wordsSetComp,
                          unknownSetComp])
    return stats

'----------------------------------------------------------------------------'
def setMetaData(fileName, epFormat, delimeter): # TODO - this should be included in the class instead
    ''''''
    parts = fileName.split(delimeter)            
    if len(epFormat) == len('S00E00'):
        for x in range(len(parts)):
            eps = [char for char in parts[x]]
            if eps[0] == 'S' and eps[3] == 'E':
                try:
                    float(eps[1])
                    float(eps[2])
                    float(eps[4])
                    float(eps[5])
                    break
                except ValueError:
                    continue
                
        sNo = '0' + eps[1] + eps[2]
        eNo = '0' + eps[4] + eps[5]
                
    elif len(epFormat) == len('000'):
        for x in range(len(parts)):
            eps = [char for char in parts[x]]
            try:
                float(eps[0])
                float(eps[1])
                float(eps[2])
                break
            except ValueError:
                continue

        sNo = '001'
        eNo = eps[0] + eps[1] + eps[2]
    
    return sNo, eNo

'----------------------------------------------------------------------------'
def writeData(inputData, fileName, sheetName, writeIndex):
    ''''''
    # prepare the Excel spreadsheets and write the lists to them https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.ExcelWriter.html
    writer = pd.ExcelWriter(fileName, engine='openpyxl')
    inputData.to_excel(writer, sheet_name=sheetName, index=writeIndex)
    writer.save()