import PySimpleGUI as sg
import pandas as pd
import os

from subscope.package.Processing import CreateDeck as cd
from subscope.package.Processing import AddCards as ac
from subscope.package.Processing import RemoveCards as rc
from subscope.package.Processing import DeckStats as ds
from subscope.package.Processing import DeleteDeck as dd
from subscope.package.options.options import Options

def deckManagement(deckList, buttons):
    headings = [[sg.Text('Manage Decks', font='any 14')],
                [sg.Text('Deck List', font='any 11')]]
                      
    deckList = [*[[sg.Radio(deckList[x],
                            group_id=1,
                            enable_events=True,
                            key=deckList[x])]
                  for x in range(len(deckList))]]
    
    buttons = [*[[sg.Button(buttons['name'][x],
                            size=(16,1),
                            key=buttons['key'][x],
                            disabled=buttons['disabled'][x])]
                 for x in range(len(buttons))]]
    
    backButton = [[sg.Button('Back')]]
    
    deckManagement = [[sg.Column(headings)],
                      [sg.Column(deckList, size=(150,190), scrollable=True ),
                       sg.Column(buttons, vertical_alignment='top')],
                      [sg.Column(backButton)]]

    return deckManagement


def manageDecks():

    # Read in the deck list
    deckFolder = Options.deck_folder_path()
    deckList = os.listdir(deckFolder)

    # Get all the source folders
    sourceFolder = Options.subtitles_folder_path()
    wordSources = next(os.walk(sourceFolder))[1]
    
    buttons = pd.DataFrame(
        columns=('name',               'key',      'disabled', 'action',    'inputs'),
          data=[['Create New Deck',    '-CREATE-', ''  ,       cd.createUI, wordSources],
                ['Add Cards',          '-ADD-',    True,       ac.addUI,    wordSources],
                ['Remove Cards',       '-REMOVE-', True,       rc.removeUI, deckFolder ],
                ['Deck Stats',         '-STATS-',  True,       ds.statsUI,  None       ],
                ['Delete Deck',        '-DELETE-', True,       dd.deleteUI, deckFolder ]])
                       
    # Main UI Window
    wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttons))
    
    while True:
        event, values = wDeckManagement.Read()
        if event in [None, 'Exit', 'Back']:
            break

        # If a deck is selected, enable the buttons
        if event in deckList:
            deckName = event
            for x in range(len(buttons)):
                wDeckManagement.Element(buttons['key'][x]).update(disabled=False)

        # If a button is pressed, open the appropriate UI
        if event in list(buttons['key']):
            wDeckManagement.Hide()
            
            for x in range(len(buttons)):
                if event == buttons['key'][x]:
                    if buttons['inputs'][x] == None:
                        buttons['action'][x](buttons['inputs'][x])
                    else:
                        buttons['action'][x](deckName, buttons['inputs'][x])
                
            # Update the deck list and the window to show any changes
            deckList = os.listdir(deckFolder)
            wDeckManagement = sg.Window('Deck Management', layout=deckManagement(deckList, buttons), finalize=True)
            wDeckManagement.UnHide()
            
    wDeckManagement.Close()
    
    return


if __name__ == '__main__':
    manageDecks()