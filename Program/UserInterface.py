# -*- coding: utf-8 -*-
# create a user interface
# button to bring up selection of the subtitle files
# output panel with subtitle analysis for the selected files

# from: ExampleWindowManagement
import os
import pandas as pd
import PySimpleGUI as sg

import SubsAnalysisFunction as saf
import SubsAnalysisClasses as sac
import UIScreens as uis
from SRS import EventReviewCards as erc

from Parsing import IchiranParse as ip
from Processing import ParsedAnalysis as pa

sg.theme('BlueMono')

windowSplash = sg.Window('Main Menu', layout=uis.splashScreen())

# Start UI loop
while True:
    event, values = windowSplash.Read()
    if event is None or event == 'Exit':
        break
    
    if event == 'Review Cards':
        # Go to SRS deck selection
        # TODO default location of 'Decks' - have an option for the user to select a different folder
        folderPath = 'C:/Users/steph/OneDrive/App/Japanese App/User Data/SRS/Decks' 
        deckList, deckKeys = erc.getDecks(folderPath)
        
        windowDeckMenu = sg.Window('Deck Menu', layout=erc.deckScreen(deckList), return_keyboard_events=True)
        windowSplash.Hide()
        
        # Initialise variables outside of the loop
        x = 0
        state = 'Front'
        while True:
            event, values = windowDeckMenu.Read()
            print('event: ', event) # for debugging the state of the cards
            
            if event is None or event == 'Exit' or event == 'Back':
                break
            
            # TODO
            # Add the algorithm for updating the ease value
            # Track how many of each type of card has been reviewed against the user limits
            # Update review dates in the deck file
            if event in deckKeys:
                # If a deck is selected, load up the cards for that deck
                deckNo = deckKeys.index(event)
                windowDeckMenu.Element('-DECK-').Update(deckList[deckNo])
                deck = pd.read_csv(folderPath + '/' + deckList[deckNo], sep='\t')
                
                reviewLimit = 5 # Add input boxes for this beside the decks
                today = erc.getDate()
                reviewDeck = deck[deck['nextReview'] != 0]  
                reviewDeck = reviewDeck[reviewDeck['nextReview'] <= today]
                reviewDeck = reviewDeck[:reviewLimit]
                
                newLimit = 2
                newDeck = deck[deck['nextReview'] == 0]
                newDeck = newDeck[:newLimit]

                deck = reviewDeck.append(newDeck)
                deck = deck.sample(frac=1).reset_index(drop=True) # Used to randomise the order of the cards

                erc.setFlip(windowDeckMenu, False)
         
                event = 'Front'
            
            # Show the back of the card when the button is pressed, disable the flip button, and enable the response buttons
            if event == 'Flip':
                state = 'Rear'
                erc.setCardDetails(windowDeckMenu, state, deck, x)
                erc.setFlip(windowDeckMenu, True)
                erc.setButtons(windowDeckMenu, False)
            
            # Check if the user has pressed a key/button and return values
            q, event, x = erc.userResponse(windowDeckMenu, event, state, x)
            
            # Must be after the flip and back display - loop only runs when the UI is interacted with
            if event == 'Front':
                # Show front of first card
                if len(deck['wordJapanese']) == 0:
                    print('No new cards, or reviews in this deck')
                    erc.setFlip(windowDeckMenu, True) # Disable flip button
                    
                elif x >= len(deck['wordJapanese']):
                    state = 'Done'
                    erc.setCardDetails(windowDeckMenu, state, deck, 0) # update cards to 'Done' state
                    erc.setButtons(windowDeckMenu, True) # Disable response buttons
                    erc.setFlip(windowDeckMenu, True) # Disable flip button
                    
                else:
                    state = event
                    erc.setCardDetails(windowDeckMenu, state, deck, x)
                    erc.setFlip(windowDeckMenu, False)
            
        windowDeckMenu.close()
        windowSplash.UnHide()
        
    if event == 'Change Settings':
        # TODO update all of the options heading names
        mainOptions = ['Option Group 1', 'Option Group 2', 'Option Group 3']
        subOptions  = ['', '', '', ''] # empty elements to make sure the keys get updated in the menus
        subOptions1 = ['a', 'b', 'c', ''] 
        subOptions2 = ['d', '',  '',  '']
        subOptions3 = ['e', 'f', 'g', 'h']
        
        allOptions = pd.DataFrame()
        groupOptions = [subOptions1, subOptions2, subOptions3]
        allOptions = allOptions.append(groupOptions, ignore_index=True)
        
        mainOptionsKeys = []
        for i in range(len(mainOptions)):
            mainOptionsKeys.append(f'-OPTIONS- {i}')
        
        windowDeckSettings = sg.Window('Deck Menu', layout=uis.settingsScreen(mainOptions, subOptions))
        windowSplash.Hide()
        
        while True:
            event, values = windowDeckSettings.Read()
            if event is None or event == 'Exit' or event == 'Back':
                break
            if event in mainOptionsKeys:
                menuNo = mainOptionsKeys.index(event)
                
                for x in range(len(allOptions.loc[menuNo,:])):
                    windowDeckSettings.Element(f'-SUBOPTIONS- {x}').Update(value=allOptions.loc[menuNo,x])
                
        windowDeckSettings.close()
        windowSplash.UnHide()
            
    if event == 'Browse Database':
        # TODO currently just a placeholder window
        windowDeckSettings = sg.Window('Database Menu', layout=uis.databaseScreen())
        print('yep2')
        
        windowSplash.Hide()
        windowDatabase = sg.Window('Database Menu', layout=uis.databaseScreen())
        
        while True:
            event, values = windowDatabase.Read()
            if event is None or event == 'Exit' or event == 'Back':
                break
            
        windowDatabase.close()
        windowSplash.UnHide()
        
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        # Get a list of files in folder
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [f
                  for f in file_list
                  if os.path.isfile(os.path.join(folder, f))
                  and f.lower().endswith(('.srt'))
                  or os.path.isfile(os.path.join(folder, f))
                  and f.lower().endswith(('.ass'))]

        # initialise the subtitle analysis window
        windowAnalysis = sg.Window('File Analysis').Layout(uis.subAnalysisWindow(fnames))
        windowSplash.Hide()
    
        while True:
            event, values = windowAnalysis.Read()
            if event is None or event == 'Exit' or event == 'Back':
                break
            if event == 'Select All':
                for i in range(len(fnames)):
                    windowAnalysis.Element(f"-SUBTITLES- {i}").Update(value=True)
            if event == 'Deselect All':
                for i in range(len(fnames)):
                    windowAnalysis.Element(f"-SUBTITLES- {i}").Update(value=False)
            if event == "-COMP-":
                if values["-COMP-"] == '': # to avoid an error with trying to divide by zero when deleting input
                    continue
                else:
                    comprehension = int(values["-COMP-"])
                    
            if event == 'Update Statistics':
                # TODO add prgress readout like in the 'Update Database' section
                if values["-COMP-"] == '': # set a default for the comprehension score if the user doesn't input one
                    comprehension = 70
                    windowAnalysis.Element("-COMP-").Update(value=comprehension)
                    
                # Only analyse files if they are selected
                fnamesSelect = []
                for i in range(len(fnames)):
                    if values[f"-SUBTITLES- {i}"] == True:
                        fnamesSelect.append(fnames[i])
                    else:
                        continue
                
                if fnamesSelect == []:
                    # TODO add message to tell user they need to select something (maybe another window?)
                    continue
                else:
                    ip.parseWrapper(folder, fnamesSelect, file_list)
                    
                    # For every specified file, create a list containing the names of the analysed text files
                    dataFiles = []
                    for x in range(len(fnamesSelect)):
                        fnamesSelect[x] = fnamesSelect[x].split('.')
                        del fnamesSelect[x][-1]
                        fnamesSelect[x] = '.'.join(fnamesSelect[x])
                        fnamesSelect[x] = fnamesSelect[x] + '_full.txt'
                        dataFiles.append(fnamesSelect[x])
                    
                    # Read each of the files to be analysed and combine into a single table
                    outputTable = pd.DataFrame()
                    for x in range(len(fnamesSelect)):
                        fullTable = pd.read_csv(folder + '/' +  fnamesSelect[x], sep='\t')
                        outputTable = outputTable.append(fullTable)
                    outputTable = outputTable.reset_index(drop=True)
                    
                    # Analyse the combined table and return the stats, then update the UI to display the results
                    stats = pa.prepStats(outputTable, 1, '==',  comprehension)
                    uis.displayStats(windowAnalysis, stats)
                    
            # TODO: still uses the old SubsAnalysisFunction instead of IchiraParse - needs rewriting
            # TODO: not sure the use of the SubAnalysisClasses class is the most appropriate way to do it - review
            if event == 'Add To Database':
                # Check which files have been marked for adding to the database
                fnamesSelect = []
                output = []
                stats = []
                metaData = []
                wordDatabase = pd.DataFrame([])
                statsDatabase = pd.DataFrame([])
                for i in range(len(fnames)):
                    if values[f"-SUBTITLES- {i}"] == True:
                        fnamesSelect.append(fnames[i])
                    else:
                        continue
                
                if fnamesSelect == []:
                    # TODO add message to tell user they need to select something (maybe another window?)
                    continue
                
                for x in range(len(fnamesSelect)):
                    print('Analysing:', x+1, '/', len(fnamesSelect))
                    fileName = fnamesSelect[x]
                    fname = [fnamesSelect[x]]
                    showName = values['-showName-']
                   
                    # TODO there must be an easier way to do the epFormat and delimeter sections
                    # epFormat
                    if values['-epFormat_S00E00-'] == True: 
                        epFormat = 'S00E00'
                    elif values['-epFormat_000-'] == True:
                        epFormat = '000'
                        
                    # delimeter
                    if values['-delimeter_1-'] == True:
                        delimeter = '.'
                    elif values['-delimeter_2-'] == True:
                        delimeter = ','
                    elif values['-delimeter_3-'] == True:
                        delimeter = '_'

                    # analyse a single episode
                    sNo, eNo = saf.setMetaData(fileName, epFormat, delimeter) # TODO parse this into the metaData class, and have that check whether it is valid

                    # TODO returns values, but the words lists aren't lists, just the text summary
                    output = saf.prepWords(folder, fname, 'Top2k.xlsx')
                    stats = saf.subStats(output, 'All Words', 'AW Freq', 'Unknown', 'Unk Freq', '>=', 10, 70) # TODO comprehension just set to 70 for now

                    metaData = sac.MetaData(showName, sNo, eNo, output['All Words'],
                                            output['AW Freq'], stats[0][0], stats[0][1],
                                            stats[0][2], stats[0][3], stats[0][4],
                                            stats[0][5], stats[0][6], stats[0][7])
                    wordData, statsData = metaData.prepData()
                    
                    wordDatabase = wordDatabase.append(wordData)
                    statsDatabase = statsDatabase.append(statsData)

                # TODO could read in the database, then append the new data (fine for small data, but probably horrific as size increases)
                # TODO combine the two databases
                print('Writing to Database')
                saf.writeData(wordDatabase, 'wordDatabase.xlsx', 'Words', True)
                saf.writeData(statsDatabase, 'statsDatabase.xlsx', 'Stats', True)
                # TODO Once the data is read in, order the database
                print('Done!')
                
        windowAnalysis.Close()
        windowSplash.UnHide()
windowSplash.Close()