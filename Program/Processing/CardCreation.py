# -*- coding: utf-8 -*-

import pandas as pd
import ast
import os
import datetime
import random
import timeit

from Program.Processing import FindSentences as fs
from Program.Processing import ExtractAudio as ea
from Program.Options import ManageOptions as mo
from Program.Database import DataHandling as dh


def getDate():
    # Convert the Python datetime format into the numerical Excel date format
    today = str(datetime.date.today()).split('-')
    today = datetime.datetime(int(today[0]), int(today[1]), int(today[2]))
    base = datetime.datetime(1899, 12, 30)
    delta = today - base
    today = float(delta.days) + (float(delta.seconds) / 86400)

    return today


def createDeck(auto, deckName, deckFormat, newLimit, reviewLimit, source, comp):
    '''
    Create a blank deck of the specified name and format
    
    auto: True/False boolean to automatically add cards to the new deck
    deckname: Name to be used for the deck filename
    deckFormat: Format to be used for the deck (currently unused)
    '''

    # TODO: add different deckFormat options - currently just default
    blankDeck = pd.DataFrame(columns=['state', # '1' if reviewed, and not 'again', otherwise '0'
                                      'source',
                                      'fullFile',
                                      'line no',
                                      'wordJapanese',
                                      'partOfSpeech',
                                      'definition',
                                      'info',
                                      'sentence',
                                      'audioClip',
                                      'screenshot',
                                      'EF',
                                      'lastReview',
                                      'nextReview',
                                      'status']) # new, learning, known, suspended

    deckFolder = mo.getSetting('paths', 'Deck Folder')
    blankDeck.to_csv(deckFolder + '/' + deckName, index=None, sep='\t')
    
    # Update the settings file with the new deck info
    optionsFolder = mo.getSetting('paths', 'Options Folder')
    decks = pd.read_csv(optionsFolder + '/deckSettings.txt', sep='\t')
    
    # Check if user input is valid, then set limit values
    #         [Limit type,     user limit,  default limit]
    limits = [['New Limit',    newLimit,    10           ],
              ['Review Limit', reviewLimit, 50           ]]
    
    for x in range(len(limits)):
        if limits[x][1] != '':
            try:
                float(limits[x][1])
                limits[x][2] = limits[x][1]
            except:
                print('Invalid input: \"' + limits[x][1] + '\". Values must be whole numbers\n' + 
                      'Default value of ' + str(limits[x][2]) + ' used for ' + limits[x][0])    

    newDeck = pd.DataFrame([[deckName,   limits[0][2], limits[1][2]]],
                   columns=('Deck Name', limits[0][0], limits[1][0]))
    
    decks = decks.append(newDeck).reset_index(drop=True)
    decks = decks.iloc[decks['Deck Name'].str.lower().argsort()]
    decks.to_csv(optionsFolder + '/deckSettings.txt', sep='\t', index=False)    
    
    if auto == True:
        autoDeck(source, deckFolder, deckName, comp)
    
    return


def autoDeck(source, deckFolder, deckName, comp):
    # TODO: add option to create a deck from multiple sources
    database = dh.readDatabase()
    sourceDatabase = database.copy()

    # Go through the database (starting at the first episode column),
    # sort by frequency, then get words to achieve x% comprehension
    words = []
    for col in sourceDatabase.columns:
        if source in col:
            subDatabase = sourceDatabase[['reading', 'text', 'kana', 'gloss', 'status', col]]
            subDatabase = subDatabase[subDatabase[col] != 0]
            subDatabase = subDatabase.sort_values(by=[col], ascending=False, ignore_index=True)

            totalWords = subDatabase[col].sum()
            
            if comp == '':
                comp = 70
                print('No target words value input. using default of 70%')
            comprehension = int(comp)/100
            
            targetWords = round(totalWords * comprehension)
            
            # Work out how many rows are required to achieve the required cmprehension
            n = 0
            cumTotal = 0
            while cumTotal < targetWords:
                cumTotal += subDatabase[col][n]
                n+=1
            subDatabase = subDatabase.head(n)
            
            i=0
            j=0
            # Time the processing of each block of 20 and estimate the remaining duration
            startTime = timeit.default_timer()
            for y in range(len(subDatabase)):
                if subDatabase['status'][y] == 0:
                    targetWord = subDatabase['text'][y]
                    print(targetWord)
                    
                    # Check whether the word has already been added to the deck
                    # Then get card info and create the media files
                    if targetWord not in words:
                        cardInfo, wordLoc = getCardInfo(targetWord, database)
                        createMedia(wordLoc)
                        addCard(deckFolder, deckName, cardInfo)
                        words.append(targetWord)
                        
                if i >= 20:
                    passedTime = timeit.default_timer() - startTime
                    estTime = round((passedTime / j) * (len(subDatabase)-j) / 60, 1)
                    
                    print('===================================')
                    print('Rows Complete:', y, '/', len(subDatabase))
                    print('Estimated time remaining:', estTime, 'minutes')
                    print('===================================')
                    
                    i = 0
                i+=1
                j+=1
                
    return
            

def getCardInfo(targetWord, database):
    ''''''
    line = database[database['text']==targetWord].reset_index(drop=True)
    # from: https://stackoverflow.com/questions/1894269/how-to-convert-string-representation-of-list-to-a-list
    line = ast.literal_eval(line['gloss'][0])

    pos = line[0]['pos']
    gloss = line[0]['gloss']

    if 'info' in line[0]:
        info = line[0]['info']
    else:
        info = 'N/A'
    
    wordLoc = fs.findSentences(targetWord)

    # TODO: for now, just grab a random sentence, but eventually find the one with the fewest unknown words
    # TODO: I shouldn't need to use '-1' for this, but if I don't I occasionally get index errors when setting the source
    senNo = random.randint(0, len(wordLoc)-1)
    
    source = wordLoc['source'][senNo]
    fullFile = wordLoc['episode'][senNo]
    lineNo = wordLoc['line no'][senNo]
    
    sentence = wordLoc['sentence'][senNo]
    
    lineNo = str(int(wordLoc['line no'][senNo]))
    audio = wordLoc['episode'][senNo].replace('full.txt', lineNo + '.wav')
    screenshot = wordLoc['episode'][senNo].replace('full.txt', lineNo + '.jpg')
    
    startEF = 2.5
    today = getDate()
    
    cardInfo = [0, source, fullFile, lineNo, targetWord, pos, gloss, info, sentence, audio, screenshot, startEF, 0, today, 'new']
    
    # Return just the selected line, for use in making media files
    wordLoc = wordLoc[:][senNo:senNo+1].reset_index(drop=True)
        
    return cardInfo, wordLoc


def addCard(deckFolder, deckName, cardInfo):
    ''''''
    deck = pd.read_csv(deckFolder + '/' + deckName, sep='\t')
    
    if len(deck[deck['wordJapanese']==cardInfo[0]]) == 0:
        deck.loc[len(deck)] = cardInfo
        deck.to_csv(r'' + deckFolder + '/' + deckName, index=None, sep='\t', mode='w')
    else:
        print('Card already exists in deck:', cardInfo[0])
        # TODO: have option to change audio clip for the card
    return


def createMedia(wordLoc):
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    source = wordLoc['source'][0]
    video = wordLoc['episode'][0].replace('_full.txt','')
    lineNo = str(int(wordLoc['line no'][0]))
    startStamp = wordLoc['timestamp'][0][0]
    endStamp = wordLoc['timestamp'][0][1]
    
    folder = sourceFolder + '/' + source
    
    if video + '.mp4' in os.listdir(folder):
        fileType = '.mp4'
    elif video + '.mkv' in os.listdir(folder):
        fileType = '.mkv'
    else:
        fileType = ''
        
        
    if fileType != '':
        # Will only need to create the audio file for an episode once,
        # then it can be split up multiple times for the audio clips/screenshots
        if ea.checkForFiles(folder + '/Audio', video, '.mp3') == False:
            ea.createAudio(folder, video, fileType)
        
        if ea.checkForFiles(folder + '/Video', video, '_' + lineNo + '.wav') == False:
            ea.createAudioClip(folder, video, lineNo, startStamp, endStamp) 
        
        # The trimmed video is used to get the screenshot
        if ea.checkForFiles(folder + '/Video', video, '_' + lineNo + '.mp4') == False:
            trimmedVideo = folder + '/Video/' + video + '_' + lineNo + '.mp4'
            ea.trimVideo(startStamp, endStamp, folder + '/' + video, fileType, trimmedVideo)
        
        if ea.checkForFiles(folder + '/Image', video, '_' + lineNo + '.jpg') == False:
            ea.createScreenshot(folder, video, fileType, lineNo, startStamp, endStamp)
        
    else:
        print('Video file (.mp4 or .mkv) does not exist for:', video)

    return


# TODO: add function for deleting decks
def deleteDeck(deckFolder, deckName):
    ''''''
    os.remove(deckFolder + '/' + deckName)
    return
    

'''
'----------------------------------------------------------------------------'
# Create a new deck
deckFolder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/SRS/Decks'
deckName = 'Deck1.txt'
deckFormat = 'default'

createDeck(deckFolder, deckName, deckFormat)

# Add a card to a deck
sourceFolder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles'
databaseFile = 'mainDatabase.txt'
database = pd.read_csv(sourceFolder + '/' + databaseFile, sep='\t')

targetWord = 'なに'

cardInfo, wordLoc = getCardInfo(targetWord, database, sourceFolder)

addCard(deckFolder, deckName, cardInfo)
createMedia(sourceFolder, wordLoc)
'----------------------------------------------------------------------------'
'''