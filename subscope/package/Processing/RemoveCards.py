# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import pandas as pd

from subscope.package.options.options import Options


def removeCard(deckName, deckFolder):
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


def removeUI(deckName, deckFolder):
    
    # Remove cards from selected deck. Show cards, and allow removal
    wRemoveCard = sg.Window('Remove Cards', layout=removeCard(deckName, deckFolder))
    while True:
        event, values = wRemoveCard.Read()

        if event is None or event == 'Exit':
            break
        
        # TODO: add logic for removing cards        

    wRemoveCard.close()
    
    return


if __name__ == '__main__':
    
    deckFolder = Options.deck_folder_path()
    
    deckName = 'SteinsGate.txt'
    
    removeUI(deckName, deckFolder)