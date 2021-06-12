# -*- coding: utf-8 -*-
# create a user interface
# button to bring up selection of the subtitle files
# output panel with subtitle analysis for the selected files

# from: ExampleWindowManagement
import os
import pandas as pd
import PySimpleGUI as sg

import UIScreens as uis

from Program.Parsing import IchiranParse as ip
from Program.Processing import ParsedAnalysis as pa
import Program.Subtitles.SubRetimerUI as sru

from SRS import ReviewUI as ru

sg.theme('BlueMono')

# Read in the user settings
pathSettings = {}
settingsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/pathSettings.txt'
with open(settingsPath) as settings:
    for line in settings:
        (key, val) = line.strip('\n').split('\t')
        pathSettings[key] = val

deckSettings = pd.read_csv('C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/deckSettings.txt', sep='\t').set_index('deckName')

windowSplash = sg.Window('Main Menu', layout=uis.splashScreen())

# Start UI loop
while True:
    event, values = windowSplash.Read()
    if event is None or event == 'Exit':
        break
    
    if event == 'Review Cards':
        # Go to SRS deck selection and card review
        ru.reviewCards(pathSettings, deckSettings)
        windowSplash.UnHide()
        
    if event == 'Change Settings':
        # TODO update all of the options heading names
        mainOptions = ['Option Group 1', 'Option Group 2', 'Option Group 3']
        subOptions  = ['',  '',  '',  '' ] # empty elements to make sure the keys get updated in the menus
        subOptions1 = ['a', 'b', 'c', '' ] 
        subOptions2 = ['d', '',  '',  '' ]
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
            
    if event == 'Retime Subtitles':
        windowSplash.Hide()
        sru.subRetime()
        windowSplash.UnHide()
        
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        # Get a list of files in folder
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [f for f in file_list
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
                if values["-COMP-"] != '':
                    comprehension = int(values["-COMP-"])
                    
            if event == 'Update Statistics':
                # Only analyse files if they are selected
                fnamesSelect = []
                for i in range(len(fnames)):
                    if values[f"-SUBTITLES- {i}"] == True:
                        fnamesSelect.append(fnames[i])
                
                if fnamesSelect == []:
                    print('No files have been selected.')
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
                    try:
                        comprehension = int(values['-COMP-'])
                    except:
                        print('Invalid comprehension. Using default value of 70.')
                        comprehension = 70
                        windowAnalysis.Element('-COMP-').update(value=comprehension)
                        
                    
                    stats = pa.prepStats(outputTable, 1, '==',  comprehension)
                    uis.displayStats(windowAnalysis, stats)
                
        windowAnalysis.Close()
        windowSplash.UnHide()
windowSplash.Close()