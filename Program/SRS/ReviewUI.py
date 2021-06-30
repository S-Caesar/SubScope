# -*- coding: utf-8 -*-

# ReviewUI: UI for the SRS review part

import pandas as pd
import PySimpleGUI as sg
import ast

from Program.SRS import ManageCards as mc

def reviewCards(mainOptions):
    deckFolder = mainOptions['Default Paths']['Deck Folder']
    deckList = mc.getDecks(deckFolder)
    
    sourceFolder = mainOptions['Default Paths']['Source Folder']
    
    # Placeholder - will be the sentence for each card
    parts = [['']*10,
             ['']*10]
    
    pos = [['']*10,
           ['']*10]
    
    glossDisplay = ''
    
    glossEvents = []
    for x in range(len(parts[0])):
        glossEvents.append(f'partA{x}')
        glossEvents.append(f'partB{x}')
    
    wDeckMenu = sg.Window('Deck Menu', layout=mc.deckScreen(deckList, pos, parts, glossDisplay), return_keyboard_events=True)
    
    # Initialise variables outside of the loop
    x = 0
    state = 'Front'
    playAudio = None
    
    while True: 
        event, values = wDeckMenu.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
        
        print('Event: ', event)
        
        if event in deckList:
            # If a deck is selected, load up the cards for that deck
            deckName = deckList[deckList.index(event)]
            deck = pd.read_csv(deckFolder + '/' + deckName, sep='\t')
            deck = deck.fillna('')
            
            wDeckMenu.Element('-DECK-').Update(deckName)
            
            reviewLimit = int(mainOptions['Deck Settings']['reviewLimit'][deckName])
            newLimit = int(mainOptions['Deck Settings']['newLimit'][deckName])
            deck = mc.prepDeck(deck, reviewLimit, newLimit)

            mc.setFlip(wDeckMenu, False) # Enable flip button
     
            event = 'Front'

        
        # Show the back of the card when the button is pressed, 
        # disable the flip button, and enable the response buttons
        if event == 'Flip':
            state = 'Rear'
            
            # Get the parsed line for use with the 'hover' dictionary
            parts, pos, reading, gloss = mc.getParts(sourceFolder, deck, x)
            print(mainOptions['UI Themes']['SRS Text Colouring'])
            if mainOptions['UI Themes']['SRS Text Colouring'] == 'Off':
                pos = [['black']*10,
                       ['black']*10]
            
            # Update the details in the window
            mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, x, parts, pos)
            mc.setFlip(wDeckMenu, True)
            mc.setButtons(wDeckMenu, False)

            event = 'Audio'
        
        
        # If the user selects part of the sentence, then show the appropriate gloss
        if event in glossEvents:
            if 'partA' in event:
                line = 0
            else:
                line = 1
                
            part = int(event[5:])
            
            wordOut = reading[line][part]
            
            glossDisplay = ast.literal_eval(gloss[line][part])
            glossOut = ''
            if glossDisplay != 0:
                for y in range(len(glossDisplay)):
                    glossOut += glossDisplay[y]['pos'] + '\n'
                    glossOut += glossDisplay[y]['gloss'] + '\n\n'
            
            wDeckMenu.Element('-WORD-').update(wordOut)
            wDeckMenu.Element('-GLOSS-').update(glossOut)
        
        
        if event in ['Again', 'Hard', 'Good', 'Easy', '1', '2', '3', '4']:
            # Check if the user has pressed a key/button and return values
            q, event = mc.userResponse(wDeckMenu, event, state)


        if event == 'Update' and x < len(deck):
            # Update the card details in the deck
            # TODO: if the user selects 'Again', the card needs to be shown again
            deck = mc.mainSRS(wDeckMenu, deck, q, x)
            x+=1
            event = 'Front'
        
        
        if event == 'Front':
            # Show front of first card
            if len(deck['wordJapanese']) == 0:
                print('No new cards, or reviews in this deck')
                state = 'Done'
                mc.setFlip(wDeckMenu, True) # Disable flip button
                
            elif x >= len(deck['wordJapanese']):
                state = 'Done'
                mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, 0) # update cards to 'Done' state
                mc.setButtons(wDeckMenu, True) # Disable response buttons
                mc.setFlip(wDeckMenu, True) # Disable flip button

                # Write the updated deck back to the deck file
                deck.to_csv(deckFolder + '/' + deckName, sep='\t', index=False)
                
            else:
                state = event
                mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, x)
                mc.setFlip(wDeckMenu, False)
                
            if playAudio != None:
                # If a response is given for the card, then stop the audio
                mc.stopAudio(playAudio)
            
        
        if event == 'Audio':
            # If the audio is replayed by pressing the button, stop it first if still playing
            if playAudio != None:
                mc.stopAudio(playAudio)

            audioFile = sourceFolder + '/' + deck['source'][x] + '/' + deck['audioClip'][x]
            playAudio = mc.playAudio(audioFile, True)
    
    wDeckMenu.close()
    return


'----------------------------------------------------------------------------'
from Program.Options import ManageOptions as mo

# Read in the user settings
optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/mainOptions.txt'
mainOptions = mo.readOptions(optionsPath)

reviewCards(mainOptions)
