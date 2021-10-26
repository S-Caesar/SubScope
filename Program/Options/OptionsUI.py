# -*- coding: utf-8 -*-

# Options UI

import PySimpleGUI as sg
import pandas as pd
import os

from Program.Options import ManageOptions as mo

def wOptions(headings, keys, fullOptions):

    # Backgorund colours for the main options
    # TODO: these will need to be different for different themes...
    bgColour = ['SteelBlue1', 'SteelBlue', 'SteelBlue']
    
    # Deck settings columns
    columns = ['New Limit', 'Review Limit']
    
    # Main UI themes
    themes = ['BlueMono', 'Dark2', 'DarkBlue14', 'DarkGrey4',
              'DarkGrey5', 'DarkRed', 'DarkTeal6', 'Default',
              'Green', 'LightBrown11', 'LightBrown9']
    
    # SRS Colouring options
    colouring = ['On', 'Off']
    
    # Main buttons
    buttons = ['Back', 'Apply Changes']
    
    
    # Main options column
    mainOptions = [[sg.Text(headings[x],
                            enable_events=True,
                            size=(11,1),
                            pad=(0,6),
                            key=f'-MAIN-{x}-',
                            relief='raised',
                            background_color=bgColour[x])]
                   for x in range(len(headings))]
   
    # Sub options column
    subHeadings = [[sg.Text(fullOptions[0]['Option'][x],
                            size=(15,1),
                            pad=(0,6),
                            key=f'-SUB-{x}-')]
                   for x in range(len(fullOptions[0]['Option']))]
    
    # Sub option, input box with the current path, and a button to browse
    pathOptions = []
    for x in range(len(fullOptions[0])):
        pathOptions.append([sg.In(default_text=fullOptions[0]['Setting'][x],
                                  size=(30,2),
                                  pad=(0,4),
                                  key=keys[0]+f'{x}',
                                  readonly=True),
                            sg.FolderBrowse(initial_folder=fullOptions[0]['Setting'][x])])
        
    # Deck name, new cards limit, review cards limit
    deck = []
    deck.append([sg.Text(' '*1 + columns[0] + ' '*4 + columns[1])])
    for x in range(len(fullOptions[1])):
        deck.append([sg.Text(' '*0),
                     sg.In(default_text=fullOptions[1][columns[0]][x],
                           size=(5,1),
                           pad=(0,6),
                           key=keys[1][0]+f'{x}'),
                     sg.Text(' '*7),
                     sg.In(default_text=fullOptions[1][columns[1]][x],
                           size=(5,1),
                           pad=(0,6),
                           key=keys[1][1]+f'{x}')])
    
    # Theme option, drop down with options
    themeOptions = [[sg.Combo(themes,
                              default_value=fullOptions[2]['Setting'][0],
                              pad=(0,6),
                              key=keys[2]+'0')],
                    [sg.Combo(colouring,
                              default_value=fullOptions[2]['Setting'][1],
                              pad=(0,6),
                              key=keys[2]+'1')]]
    
    # Main buttons
    buttons = [[sg.Button(buttons[0]),
                sg.Button(buttons[1])]]
    
    # main layout: main options headings, sub options headings, settings
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
    mLookup = pd.DataFrame(
        [['paths',  '-MAIN-0-', 'Default Paths', '-PATHS-',  '-PATHOPTIONS-',                 'Option',    0,      'dict',  'defaultPaths.txt' ],
         ['decks',  '-MAIN-1-', 'Deck Settings', '-DECKS-',  ['-NEWLIMIT-', '-REVIEWLIMIT-'], 'Deck Name', 1,      'table', 'deckSettings.txt' ],
         ['themes', '-MAIN-2-', 'UI Themes',     '-THEMES-', '-THEMEOPTIONS-',                'Option',    2,      'dict',  'themesUI.txt'     ]],
 columns=('lookup', 'mainKey',  'mainName',      'subKey',   'subOptionKey',                  'subName',  'group', 'type',  'fileName'))
    
    headings = mLookup['mainName'].tolist()
    keys = mLookup['subOptionKey'].tolist()
    
    # Read option files into a single list, and check the length of each file
    optionNo = []
    fullOptions = []
    for x in range(len(mLookup)):
        options = mo.readOptions(mLookup['lookup'][x])
        optionNo.append(len(options))
        fullOptions.append(options)
    maxNo = max(optionNo)
        
    uOptions = sg.Window('Options', layout=wOptions(headings, keys, fullOptions))
    
    # Start UI loop
    while True:
        event, values = uOptions.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
        
        # Find the row of the selected heading
        target = mLookup[mLookup['mainKey'] == event].reset_index(drop=True)
        if len(target['mainName']) != 0 and target['mainName'][0] in headings:
            
            # Colour the selected heading differently
            for mainKey in mLookup['mainKey']:
                if mainKey == event:
                    uOptions.Element(mainKey).Update(background_color='SteelBlue1')
                else:
                    uOptions.Element(mainKey).Update(background_color='SteelBlue')
            
            # Display the section for the selected option
            key = target['subKey'][0]
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
                    uOptions.Element(f'-SUB-{0}-').Update(value=target['subName'][0])
                    y+=1
    
                if x < optionNo[group]:
                    uOptions.Element(f'-SUB-{y}-').Update(value=fullOptions[group][subName][x])
                elif y < maxNo:
                    uOptions.Element(f'-SUB-{y}-').Update(value='')
                        
        # Write the updated options back to the options files:    
        if event == 'Apply Changes':
            for x in range(len(fullOptions)):
                groupType = mLookup['type'][x]
                if groupType == 'table':
                    for y in range(len(fullOptions[x])):
                        fullOptions[x]['New Limit'][y] = values[mLookup['subOptionKey'][x][0] + f'{y}']
                        fullOptions[x]['Review Limit'][y] = values[mLookup['subOptionKey'][x][1] + f'{y}']
                    
                else:
                    for y in range(len(fullOptions[x])):
                        fullOptions[x]['Setting'][y] = values[mLookup['subOptionKey'][x] + f'{y}']
            
                fileName = mLookup['fileName'][x]
                startPath = os.getcwd().split('\\')
                optionsPath = '/'.join(startPath[:-2]) + '/User Data/Settings/'
                fullOptions[x].to_csv(optionsPath + fileName, sep='\t', index=None)
            
            # Reread the theme in case it has been changed, and maintain the window appearance
            sg.theme(mo.getSetting('themes', 'Main Theme'))
            uOptions.Close()
            uOptions = sg.Window('Options', layout=wOptions(headings, keys, fullOptions), finalize=True)
            
    uOptions.close()
    
    return


if __name__ == '__main__':
    manageOptions()