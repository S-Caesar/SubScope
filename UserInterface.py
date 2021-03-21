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
import EventReviewCards as erc

windowSplash = sg.Window('Main Menu', layout=uis.splashScreen())

# Start UI loop
while True:
    event, values = windowSplash.Read()
    if event is None or event == 'Exit':
        break
    
    if event == 'Review Cards':
        # Go to SRS deck selection        
        folderPath = os.getcwd() + '\\Decks' # TODO default of Decks - have an option for the user to select a different folder
        deckList, deckKeys = erc.getDecks(folderPath)
        
        windowDeckMenu = sg.Window('Deck Menu', layout=erc.deckScreen(deckList), return_keyboard_events=True)
        windowSplash.Hide()
        
        while True:
            event, values = windowDeckMenu.Read()
            print('event: ', event) # for debugging the state of the cards
            
            if event is None or event == 'Exit' or event == 'Back':
                break
            
            if event in deckKeys:
                # TODO
                # Add the algorithm for updating the ease value
                # Track how many of each type of card has been reviewed against the user limits
                # Update review dates in the deck file
                x = 0
                deckNo = deckKeys.index(event)
                deck = pd.read_excel(folderPath + '\\' + deckList[deckNo], sheet_name='Sheet1')
                windowDeckMenu.Element('-DECK-').Update(deckList[deckNo])
                erc.setFlip(windowDeckMenu, False)
                event = 'Front'
            
            if event == 'Flip' and side == 'Front':
                event = 'Back'
                side = 'Back'
                erc.setCardDetails(windowDeckMenu, event, deck, x)
                erc.setButtons(windowDeckMenu, False)
            
            q, event, x = erc.userResponse(windowDeckMenu, event, x)
            
            if event == 'Front':
                # Show front of first card
                side = 'Front'
                if x >= len(deck['card1']):
                    event = 'Done'
                    erc.setCardDetails(windowDeckMenu, event, deck, 0)
                    erc.setButtons(windowDeckMenu, True)
                    erc.setFlip(windowDeckMenu, True)
                else:
                    erc.setCardDetails(windowDeckMenu, event, deck, x)
            
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
        try:
            # Get list of files in folder
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
        window2 = sg.Window('Second Window').Layout(uis.subAnalysisWindow(fnames))
        windowSplash.Hide()
    
        while True:
            event, values = window2.Read()
            if event is None or event == 'Exit' or event == 'Back':
                break
            if event == 'Select All':
                for i in range(len(fnames)):
                    window2.Element(f"-SUBTITLES- {i}").Update(value=True)
            if event == 'Deselect All':
                for i in range(len(fnames)):
                    window2.Element(f"-SUBTITLES- {i}").Update(value=False)
            if event == "-COMP-":
                if values["-COMP-"] == '': # to avoid an error with trying to divide by zero when deleting input
                    continue
                else:
                    comprehension = int(values["-COMP-"])
                    
            if event == 'Update Statistics':
                # TODO add prgress readout like in the 'Update Database' section
                if values["-COMP-"] == '': # set a default for the comprehension score if the user doesn't input one
                    window2.Element("-COMP-").Update(value=70)
                    comprehension = 70
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
                    output = saf.prepWords(folder, fnamesSelect, 'Top2k.xlsx')
                    saf.writeData(output, 'test1.xlsx', 'sheet1', False)
                    
                    # run the stats analysis, and assign the values to the UI keys
                    stats = saf.subStats(output, 'All Words', 'AW Freq', 'Unknown', 'Unk Freq', '>=', 10, comprehension)
                    window2.Element('-NoUniqueWords-').Update(value=stats[0][0])
                    window2.Element('-NoOnlyOnce-').Update(value=stats[0][1])
                    window2.Element('-NoOnlyX-').Update(value=stats[0][2])
                    window2.Element('-TotalWords-').Update(value=stats[0][3])
                    window2.Element('-TotalUnknown-').Update(value=stats[0][4])
                    window2.Element('-CompScore-').Update(value=stats[0][5])
                    window2.Element('-CompWords-').Update(value=stats[0][6])
                    window2.Element('-CompUnk-').Update(value=stats[0][7])
        
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
                
        window2.Close()
        windowSplash.UnHide()
windowSplash.Close()