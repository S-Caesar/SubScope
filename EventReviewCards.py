# Functions for the 'Review Cards' event
# Essentailly the main SRS component of the program

import os
import PySimpleGUI as sg

def deckScreen(deckList):
    # Show the list of decks, and the template for displaying card details
        deckCol = [[sg.Text('Select a desk to review:')],
                 *[[sg.Text(deckList[i], enable_events=True, size=(200,1), key=f'-DECKS {i}-')] for i in range(len(deckList))],
                   [sg.Text(' ')],
                   [sg.Button('Back')]]
        
        deckCard = [[sg.Text(size=(500,1), key='-DECK-')],
                    [sg.Text(size=(500,1), key='-FIELD1-')],
                    [sg.Text(size=(500,1), key='-FIELD2-')],
                    [sg.Text(size=(500,1), key='-FIELD3-')],
                    [sg.Text(size=(500,20), key='-FIELD4-')],
                    [sg.Text(' ' * 8),
                     sg.Button('Again', size=(10,2), disabled=True, button_color=('grey99', 'red2')),
                     sg.Button('Hard', size=(10,2), disabled=True, button_color=('grey99', 'dark orange')),
                     sg.Button('Good', size=(10,2), disabled=True, button_color=('grey99', 'green3')),
                     sg.Button('Easy', size=(10,2), disabled=True, button_color=('grey99', 'DeepSkyBlue3'))]]
        
        flipButton = [[sg.Button('Flip', size=(10,4), disabled=True)]]
        
        deckScreen = [[sg.Column(deckCol, size=(200,500)),
                       sg.VSeparator(),
                       sg.Column(deckCard, size=(500,500)),
                       sg.Column(flipButton)]]
        
        return deckScreen

def setButtons(window, state):
    # Set response buttons as active / inactive (used to prevent an error where the buttons are pressed before a deck is selected)
    window.Element('Again').Update(disabled=state) # TODO Replace strings with DataFrame values
    window.Element('Hard').Update(disabled=state)
    window.Element('Good').Update(disabled=state)
    window.Element('Easy').Update(disabled=state)
    
def setFlip(window, state):
    # Set 'Flip' button as active / inactive (used to prevent an error where the buttons are pressed before a deck is selected)
    window.Element('Flip').Update(disabled=state)

def getDecks(folderPath):
    # Check the decks folder, and retunr the list
    # TODO have a choice in the options menu to set the location of the decks folder - for now, user default location
    try:
        # Get list of files in folder
        file_list = os.listdir(folderPath)
    except:
        file_list = []
    
    deckList = [f
              for f in file_list
              if os.path.isfile(os.path.join(folderPath, f))
              and f.lower().endswith(('.xlsx'))]
    
    deckKeys = []
    for i in range(len(deckList)):
        deckKeys.append(f'-DECKS {i}-')
    
    return deckList, deckKeys

def setCardDetails(window, deck, cardState, x):
    # Select the information to display on the card screen
    states = ['Front', 'Back', 'Done']
    if cardState == states[0]:
        window.Element('-FIELD1-').Update(deck['card1'][x]) # TODO Replace strings with DataFrame values
        window.Element('-FIELD2-').Update('')
        window.Element('-FIELD3-').Update('')
        window.Element('-FIELD4-').Update('')
    elif cardState == states[1]:
        window.Element('-FIELD1-').Update(deck['card1'][x])
        window.Element('-FIELD2-').Update(deck['card2'][x])
        window.Element('-FIELD3-').Update(deck['card3'][x])
        window.Element('-FIELD4-').Update(deck['card4'][x])
    elif cardState == states[2]:
        window.Element('-FIELD1-').Update('Deck Finished') # TODO Replace strings with DataFrame values
        window.Element('-FIELD2-').Update('')
        window.Element('-FIELD3-').Update('')
        window.Element('-FIELD4-').Update('')