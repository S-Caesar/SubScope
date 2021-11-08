# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os
import pandas as pd

from Program.Processing import CardCreation as cc
from Program.Options import ManageOptions as mo


def createColumn(table):
    '''
    Convert a layout table into a layout for use in a column
    
    table:
        columns['type', 'content', default, 'font', 'size', 'key', 'group', 'line']
    '''
    
    functions = {'text':  sg.Text, 
                 'radio': sg.Radio,
                 'input': sg.Input,
                 'combo': sg.Combo}
    
    layout, line = [], []
    for x in range(len(table)):
        function = functions[table['type'][x]]

        if table['type'][x] == 'radio':
            element = function(table['content'][x],
                               font=table['font'][x],
                               size=table['size'][x],
                               key=table['key'][x],
                               default=table['default'][x],
                               group_id=table['group'][x])            

        else:
            element = function(table['content'][x],
                               font=table['font'][x],
                               size=table['size'][x],
                               key=table['key'][x])
        
        # Append to the line; if the next element is on a new line,
        # append the line to the layout, and start a new line
        line.append(element)
        if x < len(table)-1:
            if table['line'][x+1] == 'next' or x+1 == len(table):
                layout.append(line)
                line = []
        else:
            layout.append(line)
    
    return layout


def createDeck(cardFormats, wordSources):
    
    main = pd.DataFrame(
        columns=('type',    'content',          'default',  'font',     'size',         'key',          'group',    'line'),
        data = [['text',    'Create Deck',      '',         'any 14',   (12, 1),        None,           '',         ''    ],
                ['radio',   'Empty Deck',       True,       '',         (None, None),   '-EMPTY-',      0,          'next'],
                ['radio',   'Autofill Deck',    '',         '',         (None, None),   '-autoCheck-',  0,          'same'],
                ['text',    'Deck Name:',       '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (12, 1),        'deckName',     '',         'same'],
                ['text',    'Card Format:',     '',         '',         (12, 1),        None,           '',         'next'],
                ['combo',   cardFormats,        '',         '',         (12, 1),        'deckFormat',   '',         'same'],
                ['text',    'New Limit:',       '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (5, 1),         'newLimit',     '',         'same'],
                ['text',    'Review Limit:',    '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (5, 1),         'reviewLimit',  '',         'same'],
                ['text',    '='*30,             '',         '',         (None, None),   None,           '',         'next']])
    mainLayout = createColumn(main)
    
    auto = pd.DataFrame(
        columns=('type',    'content',          'default',  'font',     'size',         'key',          'group',    'line'),
        data = [['text',    'Select Source:',   '',         '',         (12, 1),        None,           '',         ''    ],
                ['combo',   wordSources,        '',         '',         (12, 4),        '-source-',     '',         'same'],
                ['text',    'Target known:',    '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (3, 1),         '-comp-',       '',         'same']])    
    autoLayout = createColumn(auto)

    createDeck = [[sg.Column(mainLayout, visible=True, key='-MAIN-')],
                  [sg.Column(autoLayout, visible=True, key='-AUTO-')],
                  [sg.Column([[sg.Button('Back'), sg.Button('Create Deck')]])]]

    return createDeck


def createUI(wordSources): 
        
    # TODO: Update formats once this properly implemented
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    
    wCreateDeck = sg.Window('Deck Creation', layout=createDeck(cardFormats, wordSources))
    
    while True:
        event, values = wCreateDeck.Read()
        if event in [None, 'Exit', 'Back']:
            break
        
        wCreateDeck['-AUTO-'].update(visible=True)
        
        if event == 'Create Deck':
            # If the deck name is taken, then skip deck creation
            deckName = values['deckName'] + '.txt'
            deckFolder = mo.getSetting('paths', 'Deck Folder')
            if deckName not in os.listdir(deckFolder):
                # Create a deck and fill it with cards if auto is checked
                if values['-autoCheck-'] == False or values['-source-'] != '':
                    cc.createDeck(values['-autoCheck-'], deckName, values['deckFormat'], values['newLimit'], values['reviewLimit'], values['-source-'], values['-comp-'])
                    break
                else:
                    if values['-source-'] == '':
                        # TODO: display a message in the UI if the no source is selected
                        print('No source selected for the auto deck')
                    
            else:                
                # TODO: display a message in the UI if the deck already exists
                print('Deck already exists:', deckName)

    wCreateDeck.Close()
    
    return


if __name__ == '__main__':
    
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    wordSources = next(os.walk(sourceFolder))[1]
    
    cardFormats = ['Default', 'Alt 1', 'Alt 2']
    
    createUI(wordSources, cardFormats)