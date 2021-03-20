# Take a file with a list of words of words in the show,
# and a list of words that are known, and do maths on them
# e.g. comprehension score, no. words, no. unique words,
# words required for x% comprehension

def countWords(sign, dfInput, wordColumn, freqColumn, numberOccurances):
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


def subStats(inputDataFrame, allWords, allFreq, unknownWords, unknownFreq, sign, numberOccurnaces, inputComp):
    inputMaths = inputDataFrame.fillna(0) # create a maths version of the input DataFrame for use with count()
    noUnqiueWords = countWords('>=', inputDataFrame, allWords, allFreq, 0) # count the number of unique words
    singleWords = countWords('==', inputDataFrame, allWords, allFreq, 1) # count the number of words that only appear once
    xOccurance = countWords(sign, inputDataFrame, allWords, allFreq, numberOccurnaces) # count the number of words that appear a specified number of times
    totalWords = sum(inputMaths[allWords]) # count the total number of words
    totalKnown = int(sum(inputMaths[unknownFreq])) # count the total number of known words
    comprehension = round((totalKnown / totalWords) * 100) # calculate the current comprehension score
    wordsSetComp = round(totalWords * inputComp / 100) # calculate the number of words required for input comprehension
    return noUnqiueWords, singleWords, xOccurance, totalWords, totalKnown, comprehension, wordsSetComp