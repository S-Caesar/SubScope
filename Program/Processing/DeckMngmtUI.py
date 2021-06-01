# -*- coding: utf-8 -*-

# UI for the card creation

import PySimpleGUI as sg
import os
import pandas as pd

import CardCreation as cc


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


def createDeck(cardFormats):
    headings = [[sg.Text('Create Deck', font='any 14')]]
    
    deckName = [[sg.Text('Deck Name:'),
                sg.In(size=(20,1), key='deckName')]]
    
    cardFormat = [[sg.Text('Card Format:'),
                   sg.Combo(cardFormats, size=(20,4), enable_events=False, key='deckFormat')],
                   [sg.Button('Create Deck')]]

    createDeck = [[sg.Column(headings)],
                  [sg.Column(deckName)],
                  [sg.Column(cardFormat)]]

    return createDeck


def addCard(deckName, sortOptions, wordSources, database):
    # TODO: sort the table out to show POS, definition, etc, in separate columns
    headers = list(database.columns)
    data = database.values.tolist()       
    
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    sorting = [[sg.Text('Sort words by:'),
                sg.Combo(sortOptions, size=(20,4), enable_events=False, key='deckFormat')]]
    
    search = [[sg.Text('Start typing to find words in the database:'),
               sg.In(size=(35,0))]]
    
    sources = [[sg.Text('Select sources for cards:')],
              *[[sg.Checkbox(wordSources[i], key=f'wordSources {i}', enable_events=True, default=True)] for i in range(len(wordSources))]]

    dataSearch = [[sg.Table(values=data, headings=headers, num_rows=15, enable_events=True)],
                  [sg.Button('Add Cards')]]

    addCard = [[sg.Column(headings)],
                      
                [sg.Column(sorting),
                 sg.Column(search)],
                      
                [sg.Column(sources, size=(170,300), scrollable=True, justification='Top'),
                 sg.Column(dataSearch, size=(1000,300))]]  

    return addCard


def removeCard(deckFolder, deckName):
    deckCards = pd.read_csv(deckFolder + '/' + deckName, sep='\t')

    headers = list(deckCards.columns)
    data = deckCards.values.tolist()
    
    if len(data) == 0:
        # If there are no cards in the deck, just add placeholder text
        print('No cards in this deck')
        data = ['No cards in this deck']
    
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]    
    
    cardList = [[sg.Text('Select cards below for removal:')],
                [sg.Table(values=data, headings=headers, num_rows=15)],
                [sg.Button('Remove Cards')]]
    
    removeCard = [[sg.Column(headings)],
                  
                  [sg.Column(cardList, size=(1000,325))]]
    
    return removeCard


def changeFormat(deckName, cardFormats):
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    formatSelect = [[sg.Text('=' * 20)],
                    [sg.Text('Select card format for this deck:')],
                    [sg.Combo(cardFormats, size=(20,4))]]

    mainButtons = [[sg.Button('Update'),
                   sg.Button('Cancel')]]

    newFormat = [[sg.Text('=' * 20)],
                 [sg.Text('Or, create a new card format:')],
                 [sg.Button('Create New Format')]]

    changeFormat = [[sg.Column(headings)],
                    [sg.Column(formatSelect)],
                    [sg.Column(mainButtons)],
                    [sg.Column(newFormat)]]

    return changeFormat


def stats(deckName):
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    other = [[sg.Text('To be added')]]
    
    stats = [[sg.Column(headings)],
             [sg.Column(other)]]
    
    return stats


def deleteDeck(deckName):
    headings = [[sg.Text('Delete ' + deckName + '?')]]
    
    mainButtons = [[sg.Button('Confirm'), sg.Button('Cancel')]]
    
    deleteDeck = [[sg.Column(headings)],
                  [sg.Column(mainButtons)]]
    
    return deleteDeck


sg.theme('BlueMono')

deckFolder = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/SRS/Decks'
deckList = os.listdir(deckFolder)

cardFormats = ['Default', 'Alt 1', 'Alt 2']
sortOptions = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']

sourceFolder = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Subtitles'
wordSources = os.listdir(sourceFolder)
for x in range(len(wordSources)):
    path = sourceFolder + '/' + wordSources[x]
    if os.path.isdir(path) == False:
        wordSources[x] = ''
wordSources = [x for x in wordSources if x != '']

databaseFile = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Subtitles/mainDatabase.txt'
database = pd.read_csv(databaseFile, sep='\t')


# Main UI Window
windowDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList))

# Start UI loop
while True:
    event, values = windowDeckManagement.Read()
    if event is None or event == 'Exit':
        break
    
    if event in deckList:
        deckName = event
        
        buttons = ['add', 'remove', 'change', 'stats', 'delete']
        for item in buttons:
            windowDeckManagement.Element(item).update(disabled=False)
    
    if event == 'create':
        windowCreateDeck = sg.Window('Deck Creation', layout=createDeck(cardFormats))
        windowDeckManagement.Hide()
        while True:
            event, values = windowCreateDeck.Read()

            if event is None or event == 'Exit':
                break
            
            if event == 'Create Deck':
                deckName = values['deckName'] + '.txt'
                deckFormat = values['deckFormat']
                
                # Create a new deck
                cc.createDeck(deckFolder, deckName, deckFormat)
                
                # Update the deck list to show the new deck
                # TODO: update the deck list to show the new deck
                deckList = os.listdir(deckFolder)

                break
            
        windowCreateDeck.Close()
        windowDeckManagement.UnHide()
    
    if event == 'add':
        # Add cards to the selected deck. Show database, and allow selection.
        windowAddCard = sg.Window('Add Cards', layout=addCard(deckName, sortOptions, wordSources, database))
        windowDeckManagement.Hide()
        while True:
            event, values = windowAddCard.Read()

            if event is None or event == 'Exit':
                break
            
            sourceSelect=[]
            for x in range(len(wordSources)):
                if values[f'wordSources {x}'] == True:
                    sourceSelect.append(wordSources[x])
            
            if event == 'Add Cards':
                # Add cards currently highlighted in the table
                for x in values[1]:
                    targetWord = database['text'][x]
                    
                    # Get card info, then create the media files
                    cardInfo, wordLoc = cc.getCardInfo(targetWord, database, sourceFolder)
                    cc.addCard(deckFolder, deckName, cardInfo)
                    cc.createMedia(sourceFolder, wordLoc)
                
                print('Cards successfully added to deck.')

        windowAddCard.close()
        windowDeckManagement.UnHide()


    if event == 'remove':
        # Remove cards from selected deck. Show cards, and allow removal
        windowRemoveCard = sg.Window('Remove Cards', layout=removeCard(deckFolder, deckName))
        windowDeckManagement.Hide()
        while True:
            event, values = windowRemoveCard.Read()

            if event is None or event == 'Exit':
                break
            
            # TODO: add logic for removing cards        

        windowRemoveCard.close()
        windowDeckManagement.UnHide()

            
    if event == 'change':
        # Change the format of all cards in the selected deck
        # TODO: all of this - will come later once the SRS side is fleshed out 
        windowChangeFormat = sg.Window('Change Format', layout=changeFormat(deckName, cardFormats))
        windowDeckManagement.Hide()
        while True:
            event, values = windowChangeFormat.Read()

            if event is None or event == 'Exit' or event == 'Cancel':
                break
            
        windowChangeFormat.close()
        windowDeckManagement.UnHide()    
    
    
    if event == 'stats':
        # Display deck stats
        windowStats = sg.Window('Deck Stats', layout=stats(deckName))
        windowDeckManagement.Hide()
        while True:
            event, values = windowStats.Read()

            if event is None or event == 'Exit':
                break
            
        windowStats.close()
        windowDeckManagement.UnHide()
    
    
    if event == 'delete':
        # Delete selected deck
        windowDeleteDeck = sg.Window('Delete Deck', layout=deleteDeck(deckName))
        windowDeckManagement.Hide()
        while True:
            event, values = windowDeleteDeck.Read()

            if event is None or event == 'Exit' or event == 'Cancel':
                break                        
            
            if event == 'Confirm':
                cc.deleteDeck(deckFolder, deckName)
                windowDeleteDeck.close()
                windowDeckManagement.UnHide()

        windowDeleteDeck.close()
        windowDeckManagement.UnHide()