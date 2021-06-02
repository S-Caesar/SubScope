# Functions for the 'Review Cards' event
# Essentailly the main SRS component of the program

import os
import io
import datetime
import pandas as pd
import PySimpleGUI as sg
from PIL import Image

buttons = pd.DataFrame({'Response':     ['Flip',   'Again',  'Hard',        'Good',   'Easy'        ],
                        'Keystroke':    ['',       '1',      '2',           '3',      '4'           ],
                        'q':            ['',        0,        1,             2,        3            ],
                        'TextColour':   ['grey99', 'grey99', 'grey99',      'grey99', 'grey99'      ],
                        'ButtonColour': ['grey30', 'red2',   'dark orange', 'green3', 'DeepSkyBlue3']
                         })

cardDetails = pd.DataFrame(
    {'heading': ['wordJapanese', 'partOfSpeech', 'definition', 'info',   'sentence'],
     'width':   [34,             53,             39,           43,       34        ],
     'height':  [1,              1,              2,            2,        3         ],
     'justif':  ['centre',       'centre',       'centre',     'centre', 'centre'  ],
     'font':    ['Any 18',       'Any 12',       'Any 16',     'Any 14', 'Any 18'  ]})


def deckScreen(deckList):
    # Show the list of decks, and the template for displaying card details
    deckCol = [[sg.Text('Select a desk to review:')],
             *[[sg.Text(deckList[i], enable_events=True, size=(200,1), key=f'-DECKS {i}-')] for i in range(len(deckList))]]
               
    # TODO: the text element size needs to be changed if the font changes
    #       otherwise they end up off centre - must be a way to link them so the
    #       user can then select font sizes
    deckCard = [[sg.Text(size=(60,2), justification='center', key='-DECK-')],
               *[[sg.Text(size=(cardDetails['width'][i], cardDetails['height'][i]),
                          justification=cardDetails['justif'][i],
                          font=cardDetails['font'][i],
                          key=f'-FIELD{i}-')] for i in range(len(cardDetails))],
               
                [sg.Image(key='-IMAGE-', visible=False)],
                
                # TODO There must be a way to loop these, but I can't work it out - the *[ method puts them in a column not a row  
                [sg.Button(buttons['Response'][0], size=(10,2), disabled=True, button_color=(buttons['TextColour'][0], buttons['ButtonColour'][0])), 
                 sg.Button(buttons['Response'][1], size=(10,2), disabled=True, button_color=(buttons['TextColour'][1], buttons['ButtonColour'][1])),
                 sg.Button(buttons['Response'][2], size=(10,2), disabled=True, button_color=(buttons['TextColour'][2], buttons['ButtonColour'][2])),
                 sg.Button(buttons['Response'][3], size=(10,2), disabled=True, button_color=(buttons['TextColour'][3], buttons['ButtonColour'][3])),
                 sg.Button(buttons['Response'][4], size=(10,2), disabled=True, button_color=(buttons['TextColour'][4], buttons['ButtonColour'][4]))]]

    wordDetails = [[sg.Text(text='Click on a word in the example sentence to display the glossary information here:', size=(25,4))]]
    
    mainButtons = [[sg.Button('Back')]]
    
    deckScreen = [[sg.Column(deckCol, size=(200,700)),
                   sg.VSeparator(),
                   sg.Column(deckCard, size=(500,700)),
                   sg.VSeparator(),
                   sg.Column(wordDetails, size=(200,700))],
                   [sg.Column(mainButtons)]]
    
    return deckScreen


def getDate():
    # Convert the Python datetime format into the numerical Excel date format
    today = str(datetime.date.today()).split('-')
    today = datetime.datetime(int(today[0]), int(today[1]), int(today[2]))
    base = datetime.datetime(1899, 12, 30)
    delta = today - base
    today = float(delta.days) + (float(delta.seconds) / 86400)

    return today


def setButtons(window, state):
    # Set buttons buttons as active / inactive (used to prevent an error where the buttons are pressed before a deck is selected)
    for x in range(1, len(buttons)):
        window.Element(buttons['Response'][x]).Update(disabled=state)
    return
    

def setFlip(window, state):
    # Set 'Flip' button as active / inactive (used to prevent an error where the buttons are pressed before a deck is selected)
    window.Element(buttons['Response'][0]).Update(disabled=state)
    return


def getDecks(folderPath):
    # Check the decks folder, and return the list
    # TODO have a choice in the options menu to set the location of the decks folder - for now, use default location
    try:
        # Get list of files in folder
        file_list = os.listdir(folderPath)
    except:
        file_list = []
    
    deckList = [f for f in file_list
                if os.path.isfile(os.path.join(folderPath, f))
                and f.lower().endswith(('.txt'))]
    
    deckKeys = []
    for i in range(len(deckList)):
        deckKeys.append(f'-DECKS {i}-')
    
    return deckList, deckKeys


def setCardDetails(window, sourceFolder, cardState, deck, x):
    # Select the information to display on the card screen
    states = pd.DataFrame({'State' : ['Front',                 'Rear',                  'Done'         ],
                           'FIELD0': [deck['wordJapanese'][x], deck['wordJapanese'][x], 'Deck Finished'],
                           'FIELD1': [deck['partOfSpeech'][x], deck['partOfSpeech'][x], ''             ],
                           'FIELD2': ['',                      deck['definition'][x],   ''             ],
                           'FIELD3': ['',                      deck['info'][x],         ''             ],
                           'FIELD4': ['',                      deck['sentence'][x],     ''             ],
                           'IMAGE' : [deck['screenshot'][x],   deck['screenshot'][x],   ''             ]})
    
    if len(states.loc[states['State'] == cardState]) > 0:
        row = states.loc[states['State'] == cardState].index[0]
        window.Element('-FIELD0-').Update(states.iloc[row]['FIELD0'])
        window.Element('-FIELD1-').Update(states.iloc[row]['FIELD1'])
        window.Element('-FIELD2-').Update(states.iloc[row]['FIELD2'])
        window.Element('-FIELD3-').Update(states.iloc[row]['FIELD3'])
        window.Element('-FIELD4-').Update(states.iloc[row]['FIELD4'])
        
        if cardState != 'Done':
            image = Image.open(sourceFolder + '/' + deck['source'][x] + '/' + states.iloc[row]['IMAGE'])
            image.thumbnail((500, 500))
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            window.Element('-IMAGE-').Update(data=bio.getvalue(), visible=True)
        
        if cardState != 'Rear':
            window.Element('-IMAGE-').Update(visible=False)
            
    return
        

def userResponse(window, event, state, x):
    # Check user response, and record the q value
    q = None
    for item in ['Response', 'Keystroke']:
        if len(buttons.loc[buttons[item] == event]) > 0: # If there is a row in the df that is valid, then true
            if event == 'Flip' or state == 'Front':
                # The flip button changes the card state, so no need to update the ease values
                # Or
                # If a number is pressed, ignore it if the user is on the front of the card
                continue
            else:
                row = buttons.loc[buttons[item] == event].index[0]
                q = buttons.iloc[row]['q']
                setButtons(window, True)
                x+=1
                event = 'Front'
    return q, event, x


def mainSRS(window, deck):
    print('yep')
    return