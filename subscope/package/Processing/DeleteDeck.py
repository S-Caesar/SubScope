import PySimpleGUI as sg
import pandas as pd

from subscope.package.Processing import CardCreation as cc
from subscope.package.options.options import Options

def deleteDeck(deckName):
    headings = [[sg.Text('Delete ' + deckName + '?')]]
    
    mainButtons = [[sg.Button('Confirm'), sg.Button('Cancel')]]
    
    deleteDeck = [[sg.Column(headings)],
                  [sg.Column(mainButtons)]]
    
    return deleteDeck


def deleteUI(deckName):

    deckFolder = Options.deck_folder_path()

    # Delete selected deck
    wDeleteDeck = sg.Window('Delete Deck', layout=deleteDeck(deckName))
    while True:
        event, values = wDeleteDeck.Read()
        if event is None or event == 'Exit' or event == 'Cancel':
            break
        
        if event == 'Confirm':
            cc.deleteDeck(deckFolder, deckName)
            wDeleteDeck.close()
            
            # Remove the deck from the options file
            optionsFolder = Options.options_folder_path()
            decks = pd.read_csv(optionsFolder + '/deckSettings.txt', sep='\t')
            decks = decks[decks['Deck Name'] != deckName]
            decks.to_csv(optionsFolder + '/deckSettings.txt', sep='\t', index=False)           
            
    wDeleteDeck.close()
    
    return

if __name__ == '__main__':
    
    deckFolder = Options.deck_folder_path()
    
    deckName = 'SteinsGate.txt'    
    
    deleteUI(deckName, deckFolder)