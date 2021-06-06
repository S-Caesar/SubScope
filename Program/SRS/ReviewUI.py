# -*- coding: utf-8 -*-

# ReviewUI: UI for the SRS review part

import pandas as pd
import PySimpleGUI as sg

from Program.SRS import ManageCards as mc

def reviewCards(pathSettings, deckSettings):
    sg.theme('BlueMono')
    
    deckFolder = pathSettings['deckFolder']
    deckList = mc.getDecks(deckFolder)
    
    sourceFolder = pathSettings['sourceFolder']
    
    wDeckMenu = sg.Window('Deck Menu', layout=mc.deckScreen(deckList), return_keyboard_events=True)
    
    # Initialise variables outside of the loop
    x = 0
    state = 'Front'
    playAudio = None
    
    while True:
        event, values = wDeckMenu.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
        
        print('Event: ', event)
        
        # TODO
        # Add the algorithm for updating the ease value
        # Track how many of each type of card has been reviewed against the user limits
        # Update review dates in the deck file
        if event in deckList:
            # If a deck is selected, load up the cards for that deck
            deckName = deckList[deckList.index(event)]
            deck = pd.read_csv(deckFolder + '/' + deckName, sep='\t')
            deck = deck.fillna('')
            
            wDeckMenu.Element('-DECK-').Update(deckName)
            
            reviewLimit = deckSettings['reviewLimit'][deckName]
            newLimit = deckSettings['newLimit'][deckName]
            deck = mc.prepDeck(deck, reviewLimit, newLimit)

            mc.setFlip(wDeckMenu, False)
     
            event = 'Front'
        
        # Show the back of the card when the button is pressed, 
        # disable the flip button, and enable the response buttons
        if event == 'Flip':
            state = 'Rear'
            mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, x)
            mc.setFlip(wDeckMenu, True)
            mc.setButtons(wDeckMenu, False)

            event = 'Audio'
        
        # Check if the user has pressed a key/button and return values
        q, event, x = mc.userResponse(wDeckMenu, event, state, x)
        
        # Must be after the flip and back display - loop only runs when the UI is interacted with
        if event == 'Front':
            # Show front of first card
            if len(deck['wordJapanese']) == 0:
                print('No new cards, or reviews in this deck')
                mc.setFlip(wDeckMenu, True) # Disable flip button
                
            elif x >= len(deck['wordJapanese']):
                state = 'Done'
                mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, 0) # update cards to 'Done' state
                mc.setButtons(wDeckMenu, True) # Disable response buttons
                mc.setFlip(wDeckMenu, True) # Disable flip button
                
            else:
                state = event
                mc.setCardDetails(wDeckMenu, sourceFolder, state, deck, x)
                mc.setFlip(wDeckMenu, False)
                
            # TODO: works fine, but seems to hang up on short(?) files for some reason
            if playAudio != None:
                mc.stopAudio(playAudio)
        
        if event == 'Audio':
            audioFile = sourceFolder + '/' + deck['source'][x] + '/' + deck['audioClip'][x]
            playAudio = mc.playAudio(audioFile, True)
        
    wDeckMenu.close()
    return


'----------------------------------------------------------------------------'
# Read in the user settings
settingsPath = 'C:/Users/Steph/OneDrive/App/Japanese App/User Data/Settings/pathSettings.txt'
pathSettings = {}
with open(settingsPath) as settings:
    for line in settings:
        (key, val) = line.strip('\n').split('\t')
        pathSettings[key] = val
        
deckSettings = pd.read_csv('C:/Users/Steph/OneDrive/App/Japanese App/User Data/Settings/deckSettings.txt', sep='\t').set_index('deckName')

reviewCards(pathSettings, deckSettings)