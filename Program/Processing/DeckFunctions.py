# -*- coding: utf-8 -*-

# Functions for deck management

import PySimpleGUI as sg
import pandas as pd

def createDeck(cardFormats):
    # TODO: when creating a deck, add it to the deckSettings file
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