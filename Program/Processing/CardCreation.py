# -*- coding: utf-8 -*-

import pandas as pd
import ast
import os
import datetime
import random

from Program.Processing import FindSentences as fs
from Program.Processing import ExtractAudio as ea


def getDate():
    # Convert the Python datetime format into the numerical Excel date format
    today = str(datetime.date.today()).split('-')
    today = datetime.datetime(int(today[0]), int(today[1]), int(today[2]))
    base = datetime.datetime(1899, 12, 30)
    delta = today - base
    today = float(delta.days) + (float(delta.seconds) / 86400)

    return today


def createDeck(deckFolder, deckName, deckFormat):
    ''''''
    # Create a blank deck
    if deckName not in os.listdir(deckFolder):
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
        blankDeck.to_csv(r'' + deckFolder + '/' + deckName, index=None, sep='\t', mode='w')
        
    else:
        print('Deck already exists:', deckName)
        
    return


def getCardInfo(targetWord, database, sourceFolder):
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

    wordLoc = fs.findSentences(sourceFolder, database, targetWord)
    

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


def createMedia(sourceFolder, wordLoc):
    source = wordLoc['source'][0]
    video = wordLoc['episode'][0].replace('_full.txt','')
    lineNo = str(int(wordLoc['line no'][0]))
    startStamp = wordLoc['timestamp'][0][0]
    endStamp = wordLoc['timestamp'][0][1]
    
    folder = sourceFolder + '/' + source
    mainPath = folder + '/' + video
    
    if video + '.mp4' not in os.listdir(folder):
        print('Video file does not exist:', video + '.mp4')
        
    else:
        # Will only need to create the audio file for an episode once,
        # then it can be split up multiple times for the audio clips/screenshots
        if ea.checkForFiles(folder, video, '.mp3') == False:
            ea.createAudio(mainPath)
        
        if ea.checkForFiles(folder, video, '_' + lineNo + '.wav') == False:
            ea.createAudioClip(mainPath, lineNo, startStamp, endStamp) 
        
        # The trimmed video is used to get the screenshot
        if ea.checkForFiles(folder, video, '_' + lineNo + '.mp4') == False:
            trimmedVideo = mainPath + '_' + lineNo + '.mp4'
            ea.trimVideo(startStamp, endStamp, mainPath, trimmedVideo)
        
        if ea.checkForFiles(folder, video, '_' + lineNo + '.jpg') == False:
            ea.createScreenshot(mainPath, lineNo, startStamp, endStamp)
        
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