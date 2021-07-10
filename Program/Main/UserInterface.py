# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from Program.Options import ManageOptions as mo

from Program.SRS import ReviewUI as ru
from Program.Processing import DeckMngmtUI as dmu
from Program.Database import ImportKnown as ik
from Program.Subtitles import AddSubsUI as asu
from Program.Subtitles import SubRetimerUI as sru
from Program.Processing import SubsAnalysisUI as sau
from Program.Options import OptionsUI as ou


def mainMenu(headings, buttons):
    
    columns = []
    for x in range(len(headings)):
        columns.append([[sg.Text(headings[x])],
                         *[[sg.Button(buttons[x][i])] for i in range(len(buttons[x]))]])
    
    window = []
    for x in range(len(columns)):
        window.append(sg.Column(columns[x], vertical_alignment='t'))
        if x != len(columns)-1:
            window.append(sg.VSeperator())

    mainMenu = [window]
    
    return mainMenu


# Read in the user settings
optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/mainOptions.txt'
mainOptions = mo.readOptions(optionsPath)

sg.theme(mainOptions['UI Themes']['Main Theme'])


headings = ['Flash Cards (SRS)', 'Subtitle Management', 'Options']

buttons = [['Review Cards', 'Manage Decks', 'Import Known Words'],
           ['Add Subtitles', 'Retime Subtitles', 'Analyse Subtitles'],
           ['Change Settings']]

# NOTE: if I don't put these as strings, then the windows open when they 
#       are assigned to the list, and then won't run later
destinations = [['ru.reviewCards(mainOptions)',   'dmu.manageDecks(mainOptions)',   'ik.importKnown()'    ],
                ['asu.addSubs()',                 'sru.subRetime()',                'sau.subsAnalysisUI()'],
                ['ou.manageOptions(mainOptions)'                                                          ]]

wMainMenu = sg.Window('Main Menu', layout=mainMenu(headings, buttons))

# Start UI loop
while True:
    event, values = wMainMenu.Read()
    if event is None or event == 'Exit':
        break

    for x in range(len(buttons)):
        if event in buttons[x]:
            for y in range(len(buttons[x])):
                if event == buttons[x][y]:
                    wMainMenu.Hide()
                    eval(destinations[x][y])
         
        wMainMenu.UnHide()
wMainMenu.Close()