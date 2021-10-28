# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from Program.Main import InitialSetup as ins

from Program.Subtitles import InitialSetupUI as isu
from Program.SRS import ReviewUI as ru
from Program.Processing import DeckMngmtUI as dmu
from Program.Database import ImportKnown as ik
from Program.Subtitles import AddSubsUI as asu
from Program.Subtitles import SubRetimerUI as sru
from Program.Parsing import SubsAnalysisUI as sau
from Program.Options import OptionsUI as ou


def wMainMenu(buttons):
    columns = []
    for x in buttons:
        row = []
        for y in x:
            row.append(sg.Button(y))
        columns.append([row])
        if x != buttons[-1]:
            columns.append([[sg.Text('='*30)]])
    
    mainMenu = []
    for x in columns:
        mainMenu.append([sg.Column(x, justification='centre')])
    
    return mainMenu


def mainMenu(buttons):
    ins.initialise()

    uMainMenu = sg.Window('Main Menu', layout=wMainMenu(buttons))
    
    # Start UI loop
    while True:
        event, values = uMainMenu.Read()
        if event is None or event == 'Exit':
            break

        for x in range(len(buttons)):
            if event in buttons[x]:
                for y in range(len(buttons[x])):
                    if event == buttons[x][y]:
                        uMainMenu.Close()
                        destinations[x][y]()
            
        # Reread the main menu when returning in case the theme has been changed
        uMainMenu = sg.Window('Main Menu', layout=wMainMenu(buttons), finalize=True)
                 
    uMainMenu.Close()


if __name__ == '__main__':
    
    buttons = [['Initial Setup',      'Add Subtitles'    ],
               ['Retime Subtitles',   'Analyse Subtitles'],
               ['Import Known Words', 'Manage Decks'     ],
               ['Review Cards'                           ],
               ['Change Settings'                        ]]
    
    destinations = [[isu.initialSetup,  asu.addSubs    ],
                    [sru.subRetime,     sau.analysis   ],
                    [ik.importKnown,    dmu.manageDecks],
                    [ru.reviewCards                    ],
                    [ou.manageOptions                  ]]

    mainMenu(buttons)