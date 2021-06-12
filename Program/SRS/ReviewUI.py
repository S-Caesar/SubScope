# -*- coding: utf-8 -*-

# ReviewUI: UI for the SRS review part

import pandas as pd
import PySimpleGUI as sg
import ast

from Program.SRS import ManageCards as mc

def reviewCards(pathSettings, deckSettings):
    sg.theme('BlueMono')
    
    deckFolder = pathSettings['deckFolder']
    deckList = mc.getDecks(deckFolder)
    
    sourceFolder = pathSettings['sourceFolder']
    
    parts = [['', '', '', '', '', '', '', '', '', ''],
             ['', '', '', '', '', '', '', '', '', '']] # Placeholder - will be the sentence for each card
    
    glossDisplay = ''
    
    glossEvents = []
    for x in range(len(parts[0])):
        glossEvents.append(f'partA{x}')
        glossEvents.append(f'partB{x}')
    
    wDeckMenu = sg.Window('Deck Menu', layout=mc.deckScreen(deckList, parts, glossDisplay), return_keyboard_events=True)
    
    # Initialise variables outside of the loop
    x = 0
    state = 'Front'
    playAudio = None
    
    while True:
        # Note: Order of if statements is important. Loop only runs once when
        #       the UI is interacted with, and any changes to 'event' with a
        #       script will not re-run the loop. This means, any 'event' calls
        #       must be upstream of the if statement that checks for that call  
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
            
            reviewLimit = deckSettings['reviewLimit'][deckName]
            newLimit = deckSettings['newLimit'][deckName]
            deck = mc.prepDeck(deck, reviewLimit, newLimit)

            mc.setFlip(wDeckMenu, False) # Enable flip button
     
            event = 'Front'

        
        # Show the back of the card when the button is pressed, 
        # disable the flip button, and enable the response buttons
        if event == 'Flip':
            state = 'Rear'
            
            # Get the parsed line for use with the 'hover' dictionary
            parts, reading, gloss = mc.getParts(sourceFolder, deck, x)
            
            # Update the details in the window
            mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, x, parts)
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
        
        
        if event in ['Again', 'Hard', 'Good', 'Easy']:
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
                
            # TODO: works fine, but sometimes hangs up for some reason
            if playAudio != None:
                mc.stopAudio(playAudio)
            
        
        if event == 'Audio':
            audioFile = sourceFolder + '/' + deck['source'][x] + '/' + deck['audioClip'][x]
            playAudio = mc.playAudio(audioFile, True)
    
    wDeckMenu.close()
    return

'''
'----------------------------------------------------------------------------'
# Read in the user settings
settingsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/pathSettings.txt'
pathSettings = {}
with open(settingsPath) as settings:
    for line in settings:
        (key, val) = line.strip('\n').split('\t')
        pathSettings[key] = val
        
deckSettings = pd.read_csv('C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/deckSettings.txt', sep='\t').set_index('deckName')

reviewCards(pathSettings, deckSettings)
'''