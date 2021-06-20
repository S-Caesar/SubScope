# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from Program.Processing import DeckMngmtUI as dmu
from Program.Processing import SubsAnalysisUI as sau
from Program.Subtitles import SubRetimerUI as sru
from Program.SRS import ReviewUI as ru
from Program.Options import ManageOptions as mo
from Program.Options import OptionsUI as ou

def splashScreen(buttons, keys):
    
    buttonRow = []
    for x in range(len(buttons)):
        buttonRow.append(sg.Button(buttons[x]))
    
    # set up the subtitle selection window
    splashScreen = [[sg.Text('Review / Modify SRS Cards')],
                    
                    buttonRow,
                    
                    [sg.Text("=" * 53)],
                    
                    [sg.Text('Select a folder containing subtitle files to be analysed.')],
                    [sg.In(size=(51, 1), enable_events=True, key=keys[0]),
                     sg.FolderBrowse()]]
    
    return splashScreen


# Read in the user settings
optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/mainOptions.txt'
mainOptions = mo.readOptions(optionsPath)

sg.theme(mainOptions['UI Themes']['Main Theme'])

buttons = ['Review Cards', 'Change Settings', 'Retime Subtitles', 'Manage Decks']
keys = ['-FOLDER-']
wSplash = sg.Window('Main Menu', layout=splashScreen(buttons, keys))


# Start UI loop
while True:
    event, values = wSplash.Read()
    if event is None or event == 'Exit':
        break
    
    if event in buttons or event in keys:
        wSplash.Hide()
        if event == buttons[0]:
            # Go to SRS deck selection and card review
            ru.reviewCards(mainOptions)
            
        elif event == buttons[1]:
            # Go to options settings
            ou.manageOptions(mainOptions)
                
        elif event == buttons[2]:
            # Go to subtitle renaming
            # TODO: consider incorporating with the anaylsis selection, since they use the same selection of subtitles
            sru.subRetime()
            
        elif event == buttons[3]:
            # Go to deck management
            dmu.manageDecks(mainOptions)
            
        elif event == keys[0]:
            # With the selected folder, go to subtitle analysis
            sau.subsAnalysisUI(values[keys[0]])
    wSplash.UnHide()
wSplash.Close()