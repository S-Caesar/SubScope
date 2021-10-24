# -*- coding: utf-8 -*-

# Options UI

import PySimpleGUI as sg
import pandas as pd

from Program.Options import ManageOptions as mo

def wOptions(headings, fullOptions):

    
    bgc = ['SteelBlue1', 'SteelBlue', 'SteelBlue']
    mainOptions = [[sg.Text(headings[x], enable_events=True, size=(11,1), pad=(0,4), key=f'-MAIN-{x}-', background_color=bgc[x])] for x in range(len(headings))]
    subHeadings = [[sg.Text(fullOptions[0]['Option'][x], size=(15,1), pad=(0,6), key=f'-SUBHEADINGS-{x}-')] for x in range(len(fullOptions[0]['Option']))]
    
    keys = ['-PATHOPTIONS-', '-DECKOPTIONS-', '-THEMEOPTIONS-']

    pathOptions = []
    for x in range(len(fullOptions[0])):
        pathOptions.append([sg.In(default_text=fullOptions[0]['Setting'][x], size=(30,2), pad=(0,4), key=keys[0]+f'{x}'),
                            sg.FolderBrowse(initial_folder=fullOptions[0]['Setting'][x])])
        
    
    deck = []
    deck.append([sg.Text(' '*1 + 'New Limit' + ' '*4 + 'Review Limit')])
    for x in range(len(fullOptions[1])):
        deck.append([sg.Text(' '*0),
                     sg.In(default_text=fullOptions[1]['New Limit'][x], size=(5,1), pad=(0,6), key=keys[1]+f'{x}'),
                     sg.Text(' '*7),
                     sg.In(default_text=fullOptions[1]['Review Limit'][x], size=(5,1), pad=(0,6), key=keys[1]+f'{x}1')])
    
    
    themes = ['BlueMono', 'Dark2', 'DarkBlue14', 'DarkGrey4',
              'DarkGrey5', 'DarkRed', 'DarkTeal6', 'Default',
              'Green', 'LightBrown11', 'LightBrown9']
    themeOptions = [[sg.Combo(themes, default_value=fullOptions[2]['Setting'][0], pad=(0,6))],
                    [sg.Combo(['On', 'Off'], default_value=fullOptions[2]['Setting'][1], pad=(0,6))]]
    
    
    buttons = [[sg.Button('Back'),
                sg.Button('Apply Changes')]]
    
    wOptions = [[sg.Column(mainOptions, vertical_alignment='top'),
                 sg.VSeparator(),
                 sg.Column(subHeadings, vertical_alignment='top'),
                 sg.Column(pathOptions, size=(300, 150), key='-PATHS-', visible=True),
                 sg.Column(deck, size=(300, 150), key='-DECKS-', visible=False),
                 sg.Column(themeOptions, size=(300, 150), key='-THEMES-', visible=False)],
                [sg.Column(buttons)]]
  
    return wOptions


def manageOptions():
    
    # Prepare the main lookup table
    mLookup = pd.DataFrame([['paths',  '-MAIN-0-', 'Default Paths', '-PATHS-',  'Option',    0,      'dict' ],
                            ['decks',  '-MAIN-1-', 'Deck Settings', '-DECKS-',  'Deck Name', 1,      'table'],
                            ['themes', '-MAIN-2-', 'UI Themes',     '-THEMES-', 'Option',    2,      'dict' ]],
                    columns=('lookup', 'mainKey',  'mainName',      'subKey',   'subName',  'group', 'type'))
    
    headings = mLookup['mainName'].tolist()
    
    # Read option files into a single list, and check the length of each file
    optionNo = []
    fullOptions = []
    for x in range(len(mLookup)):
        options = mo.readOptions(mLookup['lookup'][x])
        optionNo.append(len(options))
        fullOptions.append(options)
    maxNo = max(optionNo)
        
    uOptions = sg.Window('Options', layout=wOptions(headings, fullOptions))
    
    # Start UI loop
    while True:
        event, values = uOptions.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
        
        # Find the row of the selected heading
        target = mLookup[mLookup['mainKey'] == event].reset_index(drop=True)
        if target['mainName'][0] in headings:
            key = target['subKey'][0]
            
            # Colour the selected heading differently
            for mainKey in mLookup['mainKey']:
                if mainKey == event:
                    uOptions.Element(mainKey).Update(background_color='SteelBlue1')
                else:
                    uOptions.Element(mainKey).Update(background_color='SteelBlue')            
            
            # Display the section for the selected option
            for subKey in mLookup['subKey']:
                if key == subKey:
                    uOptions[key].update(visible=True)
                else:
                    uOptions[subKey].update(visible=False)

            # Update the values in the section to match the options file
            group = target['group'][0]
            subName = target['subName'][0]
            for x in range(maxNo):
                y = x
                if target['type'][0] == 'table':
                    uOptions.Element(f'-SUBHEADINGS-{0}-').Update(value=target['subName'][0])
                    y+=1

                if x < optionNo[group]:
                    uOptions.Element(f'-SUBHEADINGS-{y}-').Update(value=fullOptions[group][subName][x])
                elif y < maxNo:
                    uOptions.Element(f'-SUBHEADINGS-{y}-').Update(value='')
                    
    uOptions.close()
    
    return


if __name__ == '__main__':
    sg.theme('BlueMono')
    manageOptions()