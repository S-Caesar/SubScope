# from: ExampleCreateClass
# create a class for handling the data for each show
class MetaData:
    '''showName, sNo, eNo, wordsList, wordsFreq, \
        noUniqueWords, noOnlyOnce, noOnlyX, totalWords, \
        totalUnknown, compScore, compWords, compUnk'''
    # Class attributes
    
    # State attributes
    def __init__(self, showName, sNo, eNo, wordsList, wordsFreq, \
                     noUniqueWords, noOnlyOnce, noOnlyX, totalWords, \
                     totalUnknown, compScore, compWords, compUnk):
        self.showName = showName
        self.sNo = sNo
        self.eNo = eNo
        self.wordsList = wordsList.values.tolist()
        self.wordsFreq = wordsFreq.values.tolist()
        
        self.noUniqueWords = noUniqueWords
        self.noOnlyOnce = noOnlyOnce
        self.noOnlyX = noOnlyX
        self.totalWords = totalWords
        self.totalUnknown = totalUnknown
        self.compScore = compScore
        self.compWords = compWords
        self.compUnk = compUnk

    # Instance method
    def prepData(self):
        # Prepare the data for writing to the database
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(index=range(len(self.wordsList)), columns=['Show', 'Series', 'Episode', 'Index'])
        df['Show'] = self.showName
        df['Series'] = self.sNo
        df['Episode'] = self.eNo
        df['Index'] = np.arange(len(self.wordsList))
        
        index = pd.MultiIndex.from_frame(df)
        
        wordData = pd.DataFrame({'Words': self.wordsList, 'Freq': self.wordsFreq}, index=index)
        
        df1 = pd.DataFrame(index=range(1), columns=['Show', 'Series', 'Episode', 'Index'])
        df1['Show'] = self.showName
        df1['Series'] = self.sNo
        df1['Episode'] = self.eNo
        df1['Index'] = np.arange(1)
        
        index = pd.MultiIndex.from_frame(df1)
        
        statsData = pd.DataFrame({'No. Unique Words': self.noUniqueWords,
                                  'No. Only Once': self.noOnlyOnce,
                                  'No. Only X': self.noOnlyX,
                                  'Total Words': self.totalWords,
                                  'Total Unknown': self.totalUnknown,
                                  'Comp. Score': self.compScore,
                                  'Comp. Words': self.compWords,
                                  'Comp. Unknown': self.compUnk}, index=index)
        
        return(wordData, statsData)