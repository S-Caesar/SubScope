# -*- coding: utf-8 -*-

# UI for the card creation

import PySimpleGUI as sg
import pandas as pd
import os

from Program.Processing import CreateDeck as cd
from Program.Processing import AddCards as ac
from Program.Processing import RemoveCards as rc
from Program.Processing import ChangeFormat as cf
from Program.Processing import DeckStats as ds
from Program.Processing import DeleteDeck as dd
from Program.Options import ManageOptions as mo

def deckManagement(deckList, buttonInfo):
    headings = [[sg.Text('Manage Decks', font='any 14')],
                [sg.Text('Deck List', font='any 11')]]
                      
    deckList = [*[[sg.Radio(deckList[x],
                            group_id=1,
                            enable_events=True,
                            key=deckList[x])]
                  for x in range(len(deckList))]]
    
    buttons = [*[[sg.Button(buttonInfo['buttonName'][x],
                            size=(16,1),
                            key=buttonInfo['key'][x],
                            disabled=buttonInfo['disabled'][x])]
                 for x in range(len(buttonInfo))]]
    
    backButton = [[sg.Button('Back')]]
    
    deckManagement = [[sg.Column(headings)],
                      [sg.Column(deckList, size=(150,190), scrollable=True ),
                       sg.Column(buttons, vertical_alignment='top')],
                      [sg.Column(backButton)]]

    return deckManagement


def manageDecks():
    
    buttonInfo = pd.DataFrame([['Create New Deck',    '-CREATE-',  ''   ],
                               ['Add Cards',          '-ADD-',     True ],
                               ['Remove Cards',       '-REMOVE-',  True ],
                               ['Change Card Format', '-CHANGE-',  True ],
                               ['Deck Stats',         '-STATS-',   True ],
                               ['Delete Deck',        '-DELETE-',  True ]],
                       columns=('buttonName',         'key',       'disabled'))

    # Read in the deck list
    deckFolder = mo.getSetting('paths', 'Deck Folder')
    deckList = os.listdir(deckFolder)

    # Get all the source folders
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    wordSources = next(os.walk(sourceFolder))[1]

    # Main UI Window
    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo))
    
    while True:
        event, values = wDeckManagement.Read()
        if event in [None, 'Exit', 'Back']:
            break

        # If a deck is selected, enable the buttons
        if event in deckList:
            deckName = event
            for x in range(len(buttonInfo)):
                wDeckManagement.Element(buttonInfo['key'][x]).update(disabled=False)

        if event in list(buttonInfo['key']):
            wDeckManagement.Hide()

            if event == '-CREATE-':
                cd.createUI(wordSources)
    
            if event == '-ADD-':
                ac.addUI(deckName, wordSources)
        
            if event == '-REMOVE-':
                rc.removeUI(deckName, deckFolder)
                      
            if event == '-CHANGE-':
                cf.changeUI(deckName)
            
            if event == '-STATS-':
                ds.statsUI(deckName)
            
            if event == '-DELETE-':
                dd.deleteUI(deckName, deckFolder)
                
            # Update the deck list and the window to show any changes
            deckList = os.listdir(deckFolder)
            wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttonInfo), finalize=True)
            wDeckManagement.UnHide()
            
    wDeckManagement.Close()
    
    return


if __name__ == '__main__':
    manageDecks()