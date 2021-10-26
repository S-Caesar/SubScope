# -*- coding: utf-8 -*-

# Functions for deck management

import PySimpleGUI as sg
import pandas as pd

def createDeck(cardFormats, wordSources):
    
    headings = [[sg.Text('Create Deck', font='any 14')]]
    
    deckName = [[sg.Text('Deck Name:', size=(12, 1)),
                sg.In(size=(20, 1), key='deckName')]]
    
    cardFormat = [[sg.Text('Card Format:', size=(12, 1)),
                   sg.Combo(cardFormats, size=(20,4), enable_events=False, key='deckFormat')]]
    
    cardLimits = [[sg.Text('New Limit:', size=(12, 1)),
                   sg.In(size=(5, 1), key='newLimit')],
                  [sg.Text('Review Limit:', size=(12, 1)),
                   sg.In(size=(5, 1), key='reviewLimit')]]
    
    spacing = [[sg.Text('='*30)]]
    
    autoCheck = [[sg.Checkbox('Automatically add cards to the deck', key='-autoCheck-')]]
    
    autoDeck = [[sg.Text('Select source:'),
                 sg.Combo(wordSources, size=(20,4), enable_events=False, key='-source-', default_value=wordSources[0])],
                [sg.Text('Required comprehension:'),
                 sg.In(70, size=(3,1), enable_events=True, key='-comp-')]]
    
    createButton = [[sg.Text('='*30)],
                    [sg.Button('Back'),
                     sg.Button('Create Deck')]]
    
    createDeck = [[sg.Column(headings)],
                  [sg.Column(deckName)],
                  [sg.Column(cardFormat)],
                  [sg.Column(cardLimits)],
                  [sg.Column(spacing)],
                  [sg.Column(autoCheck)],
                  [sg.Column(autoDeck)],
                  [sg.Column(createButton)]]

    return createDeck


def addCard(deckName, sortOptions, wordSources, database):
    # TODO: sort the table out to show POS, definition, etc, in separate columns
    headers = list(database.columns)
    data = database.values.tolist()       
    
    if len(data) == 0:
        data = ['Analyse', 'Cards', 'to', 'Add', 'Words']
    
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    sorting = [[sg.Text('Sort words by:'),
                sg.Combo(sortOptions, size=(20,4), enable_events=False, key='-SORT-')]]
    
    search = [[sg.Text('Start typing to find words in the database:'),
               sg.In(size=(35,0), key='-REFINE-'),
               sg.Button('Refresh')]]
    
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