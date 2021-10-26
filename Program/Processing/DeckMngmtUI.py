# -*- coding: utf-8 -*-

# UI for the card creation

import PySimpleGUI as sg
import os
import pandas as pd

from Program.Processing import SubMngmtUI as sm
from Program.Processing import CardCreation as cc
from Program.Processing import DeckFunctions as df
from Program.Options import ManageOptions as mo
from Program.Database import DataHandling as dh

def deckManagement(deckList, buttonInfo):
    headings = [[sg.Text('Manage Decks', font='any 14')],
                [sg.Text('Deck List', font='any 11')]]
                      
    deckList = [*[[sg.Radio(deckList[x],
                            group_id=1,
                            enable_events=True,
                            key=deckList[x])]
                  for x in range(len(deckList))]]
    
    buttons = [*[[sg.Button(buttonInfo[x][0],
                            size=(16,1),
                            key=buttonInfo[x][1],
                            disabled=buttonInfo[x][2])]
                 for x in range(len(buttonInfo))]]
    
    backButton = [[sg.Button('Back')]]
    
    deckManagement = [[sg.Column(headings)],
                      [sg.Column(deckList, size=(150,190), scrollable=True ),
                       sg.Column(buttons, vertical_alignment='top')],
                      [sg.Column(backButton)]]

    return deckManagement


def manageDecks():
    
    buttonInfo = [['Create New Deck',    '-CREATE-',  False],
                  ['Add Cards',          '-ADD-',     True ],
                  ['Remove Cards',       '-REMOVE-',  True ],
                  ['Change Card Format', '-CHANGE-',  True ],
                  ['Deck Stats',         '-STATS-',   True ],
                  ['Delete Deck',        '-DELETE-',  True ]]
    
    # TODO: Update formats once this properly implemented
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    sortOptions = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']
    
    # Read in the deck list and database
    deckFolder = mo.getSetting('paths', 'Deck Folder')
    decks = mo.readOptions('decks')
    deckList = decks['Deck Name'].tolist()
    database = dh.readDatabase()

    # Get all the source folders
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    wordSources = next(os.walk(sourceFolder))[1]

    # Main UI Window
    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo))
    
    # Start UI loop
    while True:
        event, values = wDeckManagement.Read()
        if event in [None, 'Exit', 'Back']:
            break

        # If a deck is selected, enable the buttons
        if event in deckList:
            deckName = event
            for x in range(len(buttonInfo)):
                wDeckManagement.Element(buttonInfo[x][1]).update(disabled=False)
        
        # Move to the deck creation window
        if event == '-CREATE-':
            
            wDeckManagement.Hide()
            
            # Run the create cards UI
            sm.createUI(wordSources, cardFormats)

            # Update the deck list and the window to show the new deck
            deckList = os.listdir(deckFolder)
            wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo), finalize=True)            
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
                    for x in values[0]:
                        targetWord = database['text'][x]
                        
                        # Get card info, then create the media files
                        cardInfo, wordLoc = cc.getCardInfo(targetWord, database)
                        cc.addCard(deckFolder, deckName, cardInfo)
                        cc.createMedia(wordLoc)
                    
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
                    optionsFolder = mo.getSetting('paths', 'Options Folder')
                    decks = pd.read_csv(optionsFolder + '/deckSettings.txt', sep='\t')
                    decks = decks[decks['Deck Name'] != deckName]
                    decks.to_csv(optionsFolder + '/deckSettings.txt', sep='\t', index=False)           
                    
                    # Update the deck list to remove the deleted deck
                    deckList = os.listdir(deckFolder)
                    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo), finalize=True)
                    
                    wDeckManagement.UnHide()
    
            wDeleteDeck.close()
            wDeckManagement.UnHide()
            
    wDeckManagement.Close()
    
    return



if __name__ == '__main__':
    manageDecks()