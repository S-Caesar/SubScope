# -*- coding: utf-8 -*-

# UI for the card creation

import PySimpleGUI as sg
import os
import pandas as pd
import timeit

from Program.Processing import CardCreation as cc
from Program.Processing import DeckFunctions as df
from Program.Options import ManageOptions as mo

def deckManagement(deckList, buttonInfo):
    headings = [[sg.Text('Manage Decks', font='any 14')],
                [sg.Text('Deck List', font='any 11')]]
                      
    deckList = [*[[sg.Radio(deckList[i], 1, enable_events=True, key=deckList[i])] for i in range(len(deckList))]]
    
    buttons = [*[[sg.Button(buttonInfo[i][0], key=buttonInfo[i][1], disabled=buttonInfo[i][2])] for i in range(len(buttonInfo))]]
    
    deckManagement = [[sg.Column(headings)],
                      [sg.Column(deckList, size=(150,190), scrollable=True ),
                       sg.Column(buttons, vertical_alignment='top')]]

    return deckManagement


def manageDecks():
    
    buttonInfo = [['Create New Deck',    '-CREATE-',  False],
                  ['Add Cards',          '-ADD-',     True ],
                  ['Remove Cards',       '-REMOVE-',  True ],
                  ['Change Card Format', '-CHANGE-',  True ],
                  ['Deck Stats',         '-STATS-',   True ],
                  ['Delete Deck',        '-DELETE-',  True ]]
    
    deckFolder = mo.readOptions('paths')['Deck Folder']
    deckList = os.listdir(deckFolder)
    
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    sortOptions = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']
    
    sourceFolder = mo.readOptions('paths')['Source Folder']
    wordSources = os.listdir(sourceFolder)
    for x in range(len(wordSources)):
        path = sourceFolder + '/' + wordSources[x]
        if os.path.isdir(path) == False:
            wordSources[x] = ''
    wordSources = [x for x in wordSources if x != '']
    
    databaseFile = sourceFolder + '/' + 'database.txt'
    
    database = pd.read_csv(databaseFile, sep='\t')
    
    # Main UI Window
    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo))
    
    # Start UI loop
    while True:
        event, values = wDeckManagement.Read()
        if event is None or event == 'Exit':
            break
        
        if event in deckList:
            deckName = event
            
            for x in range(len(buttonInfo)):
                wDeckManagement.Element(buttonInfo[x][1]).update(disabled=False)
        
        if event == '-CREATE-':
            wCreateDeck = sg.Window('Deck Creation', layout=df.createDeck(cardFormats, wordSources))
            wDeckManagement.Hide()
            while True:
                event, values = wCreateDeck.Read()
    
                if event is None or event == 'Exit':
                    break
                
                if event == 'Create Deck':
                    deckName = values['deckName'] + '.txt'
                    deckFormat = values['deckFormat']
                    
                    # Create a new deck
                    exists = cc.createDeck(deckFolder, deckName, deckFormat)
                    
                    # If the deck name isn't taken, then create the deck
                    # TODO: probably going to be some errors here from when I changed the options files
                    if exists == 0:
                        # Add the review and new limits to the deck options file
                        optionsFolder = mo.readOptions('paths')['Options Folder']
                        decks = pd.read_csv(optionsFolder + '/' + 'deckSettings.txt', sep='\t')
                        
                        # TODO: allow user to set limits when creating the deck
                        decks = decks.append(pd.DataFrame([deckName, 5, 100]))
                        decks.to_csv(index=False)
                        
                        # If auto is ticked, then add cards based on user selection
                        if values['-autoCheck-'] == True:
                            # TODO: add option to create a deck from multiple sources
                            source = values['-source-']
                            
                            path = sourceFolder + '/' + 'database.txt'
                            sourceDatabase = pd.read_csv(path, sep='\t')
                            
                            # Go through the database (starting at the first episode column),
                            # sort by frequency, then get words to achieve x% comprehension
                            words = []
                            for col in sourceDatabase.head():
                                if source in col:
                                    subDatabase = sourceDatabase[['reading', 'text', 'kana', 'gloss', 'status', col]]
                                    subDatabase = subDatabase[subDatabase[col] != 0.0]
                                    subDatabase = subDatabase.sort_values(by=[col], ascending=False, ignore_index=True)
        
                                    totalWords = subDatabase[col].sum()
                                    comprehension = int(values['-comp-'])/100
                                    targetWords = round(totalWords * comprehension)
                                    
                                    y = 0
                                    cumTotal = 0
                                    while cumTotal < targetWords:
                                        cumTotal += subDatabase[col][y]
                                        y+=1
                                    
                                    i=0
                                    j=0
                                    # Time the processing of each block of 20 and estimate the remaining duration
                                    startTime = timeit.default_timer()
                                    
                                    subDatabase = subDatabase.head(y)
                                    for y in range(len(subDatabase)):
                                        
                                        if subDatabase['status'][y] == 0:
                                            targetWord = subDatabase['text'][y]
                                            
                                            # Check whether the word has already been added to the deck
                                            if targetWord not in words:
                                                # Get card info, then create the media files
                                                cardInfo, wordLoc = cc.getCardInfo(targetWord, database, sourceFolder)
                                                cc.addCard(deckFolder, deckName, cardInfo)
                                                cc.createMedia(sourceFolder, wordLoc)
                                                
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
                    
                    # Update the deck list to show the new deck
                    deckList = os.listdir(deckFolder)
                    
                    # Update the window to show the added deck
                    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo), finalize=True)
    
                    break
                
            wCreateDeck.Close()
            wDeckManagement.UnHide()
        
        if event == '-ADD-':
            # Add cards to the selected deck. Show database, and allow selection.
            wAddCard = sg.Window('Add Cards', layout=df.addCard(deckName, sortOptions, wordSources, database))
            wDeckManagement.Hide()
            while True:
                event, values = wAddCard.Read()
    
                if event is None or event == 'Exit':
                    break
                
                sourceSelect=[]
                for x in range(len(wordSources)):
                    if values[f'wordSources {x}'] == True:
                        sourceSelect.append(wordSources[x])
                
                
                if event == 'Refresh':
                    
                    refine = values['-REFINE-']
                    sort = values['-SORT-']
                    
                    # TODO: allow searching in Japanese as well
                    databaseRefined = database[database['gloss'].str.contains(refine)] 
                    
                    # TODO: expand the sort options
                    if sort in sortOptions:
                        if sort == '':
                            databaseRefined.sort_values(by=['text'], inplace=True, ignore_index=True)
                        elif sort == 'Hiragana':
                            databaseRefined.sort_values(by=['kana'], inplace=True, ignore_index=True)
                        elif sort == 'Alphabet':
                            databaseRefined.sort_values(by=['gloss'], inplace=True, ignore_index=True)
                    
                    # Update the database display based on user selections
                    wAddCard.Close()
                    wAddCard = sg.Window('Add Cards', layout=df.addCard(deckName, sortOptions, wordSources, databaseRefined))
                    wAddCard.Read()
                
                if event == 'Add Cards':
                    # Add cards currently highlighted in the table
                    for x in values[1]:
                        targetWord = database['text'][x]
                        
                        # Get card info, then create the media files
                        cardInfo, wordLoc = cc.getCardInfo(targetWord, database, sourceFolder)
                        cc.addCard(deckFolder, deckName, cardInfo)
                        cc.createMedia(sourceFolder, wordLoc)
                    
                    print('Cards successfully added to deck.')
    
            wAddCard.close()
            wDeckManagement.UnHide()
    
    
        if event == '-REMOVE-':
            # Remove cards from selected deck. Show cards, and allow removal
            wRemoveCard = sg.Window('Remove Cards', layout=df.removeCard(deckFolder, deckName))
            wDeckManagement.Hide()
            while True:
                event, values = wRemoveCard.Read()
    
                if event is None or event == 'Exit':
                    break
                
                # TODO: add logic for removing cards        
    
            wRemoveCard.close()
            wDeckManagement.UnHide()
    
                
        if event == '-CHANGE-':
            # Change the format of all cards in the selected deck
            # TODO: all of this - will come later once the SRS side is fleshed out 
            wChangeFormat = sg.Window('Change Format', layout=df.changeFormat(deckName, cardFormats))
            wDeckManagement.Hide()
            while True:
                event, values = wChangeFormat.Read()
    
                if event is None or event == 'Exit' or event == 'Cancel':
                    break
                
            wChangeFormat.close()
            wDeckManagement.UnHide()    
        
        
        if event == '-STATS-':
            # Display deck stats
            wStats = sg.Window('Deck Stats', layout=df.stats(deckName))
            wDeckManagement.Hide()
            while True:
                event, values = wStats.Read()
    
                if event is None or event == 'Exit':
                    break
                
            wStats.close()
            wDeckManagement.UnHide()
        
        
        if event == '-DELETE-':
            # Delete selected deck
            wDeleteDeck = sg.Window('Delete Deck', layout=df.deleteDeck(deckName))
            wDeckManagement.Hide()
            while True:
                event, values = wDeleteDeck.Read()
    
                if event is None or event == 'Exit' or event == 'Cancel':
                    break                        
                
                if event == 'Confirm':
                    cc.deleteDeck(deckFolder, deckName)
                    wDeleteDeck.close()
                    
                    # Remove the deck from the options file
                    optionsFolder = mo.readOptions('paths')['Options Folder']
                    decks = pd.read_csv(optionsFolder + '/' + 'deckSettings.txt', sep='\t')
                    decks = decks[decks.deckName != deckName]
                    decks.to_csv(index=False)              
                    
                    # Update the deck list to remove the deleted deck
                    deckList = os.listdir(deckFolder)
                    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo), finalize=True)
                    
                    wDeckManagement.UnHide()
    
            wDeleteDeck.close()
            wDeckManagement.UnHide()
    return



if __name__ == '__main__':
    
    buttonInfo = [['Create New Deck',    '-CREATE-',  False],
                  ['Add Cards',          '-ADD-',     True ],
                  ['Remove Cards',       '-REMOVE-',  True ],
                  ['Change Card Format', '-CHANGE-',  True ],
                  ['Deck Stats',         '-STATS-',   True ],
                  ['Delete Deck',        '-DELETE-',  True ]]   
    
    manageDecks()