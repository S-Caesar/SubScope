# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os
import timeit

from Program.Processing import CardCreation as cc
from Program.Processing import DeckFunctions as df
from Program.Options import ManageOptions as mo
from Program.Database import DataHandling as dh


def createUI(wordSources, cardFormats): 
    
    database = dh.readDatabase()
    
    deckFolder = mo.getSetting('paths', 'Deck Folder')
    
    wCreateDeck = sg.Window('Deck Creation', layout=df.createDeck(cardFormats, wordSources))
    
    while True:
        event, values = wCreateDeck.Read()
        if event in [None, 'Exit', 'Back']:
            break
        
        if event == 'Create Deck':
            # If the deck name is taken, then skip deck creation
            deckName = values['deckName'] + '.txt'
            if deckName in os.listdir(deckFolder):
                print('Deck already exists:', deckName)
                break
            
            # Create a blank deck of the specified format
            cc.createDeck(deckName, values['deckFormat'], values['newLimit'], values['reviewLimit'])
            
            # If auto is ticked, then add cards based on user selection
            if values['-autoCheck-'] == True:
                # TODO: add option to create a deck from multiple sources
                source = values['-source-']
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
                        comprehension = int(values['-comp-'])/100
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
                                    cardInfo, wordLoc = cc.getCardInfo(targetWord, database)
                                    cc.createMedia(wordLoc)
                                    cc.addCard(deckFolder, deckName, cardInfo)
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
            
            break
        
    wCreateDeck.Close()
    
    return

if __name__ == '__main__':
    
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    wordSources = next(os.walk(sourceFolder))[1]
    
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    
    createUI(wordSources, cardFormats)