# -*- coding: utf-8 -*-

import PySimpleGUI as sg


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


def changeUI(deckName):
    
    # TODO: Update formats once this properly implemented
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    
    # Change the format of all cards in the selected deck
    # TODO: all of this - will come later once the SRS side is fleshed out 
    wChangeFormat = sg.Window('Change Format', layout=changeFormat(deckName, cardFormats))
    while True:
        event, values = wChangeFormat.Read()

        if event is None or event == 'Exit' or event == 'Cancel':
            break
        
    wChangeFormat.close()
    
    return


if __name__ == '__main__':
    
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    
    deckName = 'SteinsGate.txt'
    
    changeUI(deckName, cardFormats)