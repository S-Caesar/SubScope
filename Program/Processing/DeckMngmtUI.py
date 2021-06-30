# -*- coding: utf-8 -*-

# UI for the card creation

import PySimpleGUI as sg
import os
import pandas as pd

from Program.Processing import CardCreation as cc
from Program.Processing import DeckFunctions as df


def deckManagement(deckList):
    headings = [[sg.Text('Manage Decks', font='any 14')],
                [sg.Text('Deck List', font='any 11')]]
                      
    deckList = [*[[sg.Radio(deckList[i], 1, enable_events=True, key=deckList[i])] for i in range(len(deckList))]]
    
    buttons = [[sg.Button('Create New Deck', key='create')],
               [sg.Button('Add Cards', key='add', disabled=True)],
               [sg.Button('Remove Cards', key='remove', disabled=True)],
               [sg.Button('Change Card Format', key='change', disabled=True)],
               [sg.Button('Deck Stats', key='stats', disabled=True)],
               [sg.Button('Delete Deck', key='delete', disabled=True)]]
    
    deckManagement = [[sg.Column(headings)],
                      [sg.Column(deckList, size=(150,190), scrollable=True ),
                       sg.Column(buttons, vertical_alignment='top')]]

    return deckManagement



def manageDecks(mainOptions):
    deckFolder = mainOptions['Default Paths']['Deck Folder']
    deckList = os.listdir(deckFolder)
    
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    sortOptions = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']
    
    sourceFolder = mainOptions['Default Paths']['Source Folder']
    wordSources = os.listdir(sourceFolder)
    for x in range(len(wordSources)):
        path = sourceFolder + '/' + wordSources[x]
        if os.path.isdir(path) == False:
            wordSources[x] = ''
    wordSources = [x for x in wordSources if x != '']
    
    databaseFile = sourceFolder + '/' + 'mainDatabase.txt'
    database = pd.read_csv(databaseFile, sep='\t')
    
    
    # Main UI Window
    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList))
    
    # Start UI loop
    while True:
        event, values = wDeckManagement.Read()
        if event is None or event == 'Exit':
            break
        
        if event in deckList:
            deckName = event
            
            buttons = ['add', 'remove', 'change', 'stats', 'delete']
            for item in buttons:
                wDeckManagement.Element(item).update(disabled=False)
        
        if event == 'create':
            wCreateDeck = sg.Window('Deck Creation', layout=df.createDeck(cardFormats))
            wDeckManagement.Hide()
            while True:
                event, values = wCreateDeck.Read()
    
                if event is None or event == 'Exit':
                    break
                
                if event == 'Create Deck':
                    deckName = values['deckName'] + '.txt'
                    deckFormat = values['deckFormat']
                    
                    # Create a new deck
                    cc.createDeck(deckFolder, deckName, deckFormat)
                    
                    # Update the deck list to show the new deck
                    deckList = os.listdir(deckFolder)
                    
                    # Update the window to show the added deck
                    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList), finalize=True)
    
                    break
                
            wCreateDeck.Close()
            wDeckManagement.UnHide()
        
        if event == 'add':
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
    
    
        if event == 'remove':
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
    
                
        if event == 'change':
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
        
        
        if event == 'stats':
            # Display deck stats
            wStats = sg.Window('Deck Stats', layout=df.stats(deckName))
            wDeckManagement.Hide()
            while True:
                event, values = wStats.Read()
    
                if event is None or event == 'Exit':
                    break
                
            wStats.close()
            wDeckManagement.UnHide()
        
        
        if event == 'delete':
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
                    
                    # Update the deck list to remove the deleted deck
                    deckList = os.listdir(deckFolder)
                    # Update the window so the deleted deck is no longer an option
                    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList), finalize=True)
                    
                    wDeckManagement.UnHide()
    
            wDeleteDeck.close()
            wDeckManagement.UnHide()
    return