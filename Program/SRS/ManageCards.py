# -*- coding: utf-8 -*-

# Functions for the 'Review Cards' event
# Essentailly the main SRS component of the program

import os
import io
import datetime
import pandas as pd
import PySimpleGUI as sg
from PIL import Image
import simpleaudio as sa
import ast

cardDetails = pd.DataFrame({
    'Heading': ['wordJapanese', 'partOfSpeech', 'definition', 'info'  ],
    'Width':   [34,             53,             39,           43      ],
    'Height':  [1,              1,              2,            2,      ],
    'Justif':  ['centre',       'centre',       'centre',     'centre'],
    'Font':    ['Any 18',       'Any 12',       'Any 16',     'Any 14']})


buttons = pd.DataFrame({
    'Response':     ['Flip',   'Again',  'Hard',        'Good',   'Easy'        ],
    'Keystroke':    ['',       '1',      '2',           '3',      '4'           ],
    'q':            ['',        0,        1,             2,        3            ],
    'TextColour':   ['grey99', 'grey99', 'grey99',      'grey99', 'grey99'      ],
    'ButtonColour': ['grey30', 'red2',   'dark orange', 'green3', 'DeepSkyBlue3']})

def deckScreen(deckList, parts, pos, gloss):
    # Can't unpack * method in a row, so have to do it like this
    buttonRow = []
    for x in range(len(buttons)):
        buttonRow.append(sg.Button(buttons['Response'][x],
                                    size=(10,2),
                                    disabled=True,
                                    button_color=(buttons['TextColour'][x],
                                                  buttons['ButtonColour'][x])))
    

    # Calculate the length of each line for sizing of the elements
    senLen = [0, 0]
    for x in range(len(parts)):
        for y in range(len(parts[x])):
            senLen[0] = senLen[0] + len(parts[0][y])
    
    # Show the list of decks, and the template for displaying card details
    deckCol = [[sg.Text('Select a desk to review:')],
             *[[sg.Text(deckList[i], enable_events=True, size=(200,1))] for i in range(len(deckList))]]
               
    deckCard = [[sg.Text(size=(60,2), justification='center', key='-DECK-')],
               *[[sg.Text(size=(cardDetails['Width'][i], cardDetails['Height'][i]),
                          justification=cardDetails['Justif'][i],
                          font=cardDetails['Font'][i],
                          key=f'-FIELD{i}-')] for i in range(len(cardDetails))],

               *[[sg.Text(parts[0][i], enable_events=True, pad=(0,0), size=(senLen[0],1), text_color=pos[0][i], font='Any 18', key=f'partA{i}') for i in range(len(parts[0]))]],
               
               *[[sg.Text(parts[1][i], enable_events=True, pad=(0,0), size=(senLen[1],1), text_color=pos[1][i], font='Any 18', key=f'partB{i}') for i in range(len(parts[1]))]],
               
                [sg.Image(key='-IMAGE-', size=(269,269), visible=True)],
                
                buttonRow,
                
                [sg.Button('Audio', size=(10,2), disabled=True)]]

    wordDetails = [[sg.Text(text='Click on a word in the example sentence to display the glossary information below', size=(25,3))],
                   [sg.Text(text='_'*27)],
                   [sg.Text(gloss, enable_events=True, pad=(0,0), size=(18,2), font='Any 16', key='-WORD-')],
                   [sg.Text(gloss, enable_events=True, pad=(0,0), size=(21,40), font='Any 12', key='-GLOSS-')]]
    
    mainButtons = [[sg.Button('Back')]]
    
    deckScreen = [[sg.Column(deckCol, size=(200,700)),
                   sg.VSeparator(),
                   sg.Column(deckCard, size=(500,700), element_justification='c'),
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
    
    window.Element('Audio').Update(disabled=state)
    return
    

def setFlip(window, state):
    # Set 'Flip' button as active / inactive (used to prevent an error
    # where the buttons are pressed before a deck is selected)
    window.Element(buttons['Response'][0]).Update(disabled=state)
    return


def getDecks(folderPath):
    # Check the decks folder, and return the list
    try:
        file_list = os.listdir(folderPath)
    except:
        file_list = []
    
    deckList = [f for f in file_list
                if os.path.isfile(os.path.join(folderPath, f))
                and f.lower().endswith(('.txt'))]

    return deckList


def prepDeck(deck, reviewLimit, newLimit):         
    # Add any 'review' cards to the deck, observing the limit
    today = getDate()
    reviewDeck = deck[deck['nextReview'] != 0]  
    reviewDeck = reviewDeck[reviewDeck['nextReview'] <= today]
    reviewDeck = reviewDeck[:reviewLimit]
    
    # Add any 'new' cards to the deck, observing the limit
    newDeck = deck[deck['nextReview'] == 0]
    newDeck = newDeck[:newLimit]

    # Combine the review and new decks, then randomise the order
    deck = reviewDeck.append(newDeck)
    deck = deck.sample(frac=1).reset_index(drop=True)
    
    return deck


def playAudio(audioFile, play):
    waveObj = sa.WaveObject.from_wave_file(audioFile)
    playAudio = waveObj.play()
    return playAudio


def stopAudio(playAudio):
    playAudio.stop()
    return


def setCardDetails(window, sourceFolder, cardState, deck, x, parts='', pos=''):
    # Select the information to display on the card screen
    states = pd.DataFrame({'State' : ['Front',                 'Rear',                  'Done'         ],
                           'FIELD0': [deck['wordJapanese'][x], deck['wordJapanese'][x], 'Deck Finished'],
                           'FIELD1': [deck['partOfSpeech'][x], deck['partOfSpeech'][x], ''             ],
                           'FIELD2': ['',                      deck['definition'][x],   ''             ],
                           'FIELD3': ['',                      deck['info'][x],         ''             ],
                           'IMAGE' : [deck['screenshot'][x],   deck['screenshot'][x],   ''             ]})
    
    if len(states.loc[states['State'] == cardState]) > 0:
        row = states.loc[states['State'] == cardState].index[0]
        window.Element('-FIELD0-').Update(states.iloc[row]['FIELD0'])
        window.Element('-FIELD1-').Update(states.iloc[row]['FIELD1'])
        window.Element('-FIELD2-').Update(states.iloc[row]['FIELD2'])
        window.Element('-FIELD3-').Update(states.iloc[row]['FIELD3'])
        
        if cardState == 'Rear':
            for y in range(len(parts[0])):
                window.Element(f'partA{y}').Update(parts[0][y])
                window.Element(f'partB{y}').Update(parts[1][y])
                
                window.Element(f'partA{y}').Update(text_color=pos[0][y])
                window.Element(f'partB{y}').Update(text_color=pos[1][y])
        
        if cardState != 'Done':
            image = Image.open(sourceFolder + '/' + deck['source'][x] + '/' + states.iloc[row]['IMAGE'])
            image.thumbnail((475, 475))
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            window.Element('-IMAGE-').Update(data=bio.getvalue(), visible=True)
        
        if cardState != 'Rear':
            window.Element('-IMAGE-').Update(visible=False)
            
            parts = [['']*10,
                     ['']*10]
            
            pos = [['black']*10,
                   ['black']*10]
            
            for y in range(len(parts[0])):
                window.Element(f'partA{y}').Update(parts[0][y])
                window.Element(f'partB{y}').Update(parts[1][y])
                
                window.Element(f'partA{y}').Update(text_color=pos[0][y])
                window.Element(f'partB{y}').Update(text_color=pos[1][y])
    return


def getParts(sourceFolder, deck, x):
    # Get the parsed parts of the sentence, along with the glossary info
    parts = [['']*10,
             ['']*10]
    
    pos = [['black']*10,
           ['black']*10]
    
    reading = [['']*10,
               ['']*10]
    
    gloss = [['']*10,
             ['']*10]
    
    posColours = {'[n]': 'green4',
                  '[pn]': 'DarkOrange1',
                  '[prt]': 'purple3',
                  '[adv]': 'red3',
                  '[v]': 'DarkGoldenrod4',
                  '[int]': 'gray',
                  '[cop]': 'maroon3',
                  '[suf]': 'medium blue',
                  '[conj]': 'OliveDrab4'}
    
    file = pd.read_csv(sourceFolder + '/' + deck['source'][x] + '/' + deck['fullFile'][x], sep='\t')
    
    # Some timestamps will have multiple spoke lines - need to collect all of them
    parts1 = file[file['line']+1 == deck['line no'][x]].reset_index(drop=True)
    parts2 = file[file['line'] == deck['line no'][x]].reset_index(drop=True)
    parts3 = file[file['line']-1 == deck['line no'][x]].reset_index(drop=True)
    
    # Check whether the 'parts' above contain entries
    n = 0
    line = [[],[]]
    for item in [parts1, parts2, parts3]:
        if len(item) != 0 and n == 0:
            line[0] = item
            n = 1
        elif len(item) != 0 and n == 1:
            line[1] = item
    
    # Centre the sentence for each line
    for y in range(len(line)):    
        fullLen = len(parts[y])
        partsLen = len(line[y])
        whitespace = fullLen - partsLen
        startPad = round(whitespace/2)
        
        for z in range(len(line[y])):
            parts[y][z+startPad] = line[y]['text'][z]
            reading[y][z+startPad] = line[y]['reading'][z]
            gloss[y][z+startPad] = line[y]['gloss'][z]
            
            posDict = ast.literal_eval(line[y]['gloss'][z])
            
            if posDict != 0:
                if ',' in posDict[0]['pos']:
                    # If there are multiple categories, just use the first one
                    temp = posDict[0]['pos'].split(',')
                    posDict[0]['pos'] = temp[0] + ']'
                    
                if posDict[0]['pos'] in ['[v1]', '[v5r]', '[v5s]', '[v5k-s]', '[vi]', '[vt]', '[vs]', '[vs-i]', '[vk]']:
                    # If it's a verb group, just make it a verb
                    posDict[0]['pos'] = '[v]'
                
                if posDict[0]['pos'] in posColours:
                    pos[y][z+startPad] = posColours[posDict[0]['pos']]
            
    return parts, pos, reading, gloss


def userResponse(window, event, state):
    # Check user response, and record the q value
    q = None
    for item in ['Response', 'Keystroke']:
        # Check if the event is in the 'buttons' table
        if len(buttons.loc[buttons[item] == event]) > 0:
            if event == 'Flip' or state == 'Front':
                # The flip button changes the card state, so no need to update the ease values
                # Or
                # If a number is pressed, ignore it if the user is on the front of the card
                continue
            else:
                row = buttons.loc[buttons[item] == event].index[0]
                q = buttons.iloc[row]['q']
                setButtons(window, True)
                event = 'Update'
    return q, event
    

def updateCard(EF, q, oldInterval):
    # Update card stats
    newEF = EF+(0.1-(3-q)*(0.1+(3-q)*0.06))
    if newEF < 1.3:
        newEF = 1.3
    
    if q == 0:
        newInterval = 1
    else:
        newInterval = round(oldInterval*newEF)
        
    return newEF, newInterval


def mainSRS(window, deck, q, x):
    if deck['lastReview'][x] == 0:
        # Card is new, so just set the interval to 1
        oldInterval = 1
    else:
        # TODO: consider making the interval the current date, rather than the original planned review date
        oldInterval = deck['nextReview'][x] - deck['lastReview'][x]
    
    newEF, newInterval = updateCard(deck['EF'][x], q, oldInterval)
    
    today = getDate()
    deck.loc[deck.index[x], 'lastReview'] = today
    deck.loc[deck.index[x], 'nextReview'] = today + newInterval
    deck.loc[deck.index[x], 'EF'] = newEF
    deck.loc[deck.index[x], 'status'] = 'learning'
    
    return deck