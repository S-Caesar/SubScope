# -*- coding: utf-8 -*-

import PySimpleGUI as sg

def stats(deckName):
    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    other = [[sg.Text('To be added')]]
    
    stats = [[sg.Column(headings)],
             [sg.Column(other)]]
    
    return stats


def statsUI(deckName):
    
    # Display deck stats
    wStats = sg.Window('Deck Stats', layout=stats(deckName))
    while True:
        event, values = wStats.Read()

        if event is None or event == 'Exit':
            break
        
    wStats.close()
    
    return


if __name__ == '__main__':
    
    deckName = 'SteinsGate.txt'
    
    statsUI(deckName)