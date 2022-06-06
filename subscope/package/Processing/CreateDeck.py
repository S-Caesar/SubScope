import PySimpleGUI as sg
import os
import pandas as pd

from subscope.package.Processing import CardCreation as cc
from subscope.package.options.options import Options


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
                               group_id=table['group'][x],
                               enable_events=True)            

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


def createDeck():

    sourceFolder = Options.subtitles_folder_path()
    wordSources = next(os.walk(sourceFolder))[1]
    
    wWidth = 220
    
    main = pd.DataFrame(
        columns=('type',    'content',          'default',  'font',     'size',         'key',          'group',    'line'),
        data = [['text',    'Create Deck',      '',         'any 14',   (12, 1),        None,           '',         ''    ],
                ['radio',   'Empty Deck',       True,       '',         (None, None),   '-emptyCheck-', 0,          'next'],
                ['radio',   'Autofill Deck',    '',         '',         (None, None),   '-autoCheck-',  0,          'same'],
                ['text',    'Deck Name:',       '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (12, 1),        'deckName',     '',         'same'],
                ['text',    'New Limit:',       '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (5, 1),         'newLimit',     '',         'same'],
                ['text',    'Review Limit:',    '',         '',         (12, 1),        None,           '',         'next'],
                ['input',   '',                 '',         '',         (5, 1),         'reviewLimit',  '',         'same']])
    mainLayout = createColumn(main)
    
    auto = pd.DataFrame(
        columns=('type',    'content',               'default',  'font',     'size',         'key',          'group',    'line'),
        data = [['text',    'Source:',               '',         '',         (6, 1),         None,           '',         ''    ],
                ['combo',   wordSources,             '',         '',         (17, 4),        '-source-',     '',         'same'],
                ['text',    'Target Comprehension:', '',         '',         (17, 1),        None,           '',         'next'],
                ['input',   '',                      '',         '',         (3, 1),         '-comp-',       '',         'same']])    
    
    autoLayout = createColumn(auto)
    
    statusBar = [[sg.Text('', key='-statusBar-', size=(wWidth, 30))]]
    
    createDeck = [[sg.Column(mainLayout, key='-MAIN-', size=(wWidth, 140))],
                  [sg.Column(autoLayout, visible=False, key='-AUTO-', size=(wWidth, 50)),
                   sg.Column([[sg.Text('')]], visible=False, key='-EMPTY-', size=(wWidth, 0))],
                  [sg.Column(statusBar, key='-STATUS-', size=(wWidth, 30))],
                  [sg.Column([[sg.Button('Back'), sg.Button('Create Deck')]])]]

    return createDeck


# TODO: included deckName as an input so the management UI can be simplified - ideally get rid of it
def createUI(deckName):
    
    status = ['', 'Deck name already exists: ', 'No auto deck source selected']
    
    wCreateDeck = sg.Window('Deck Creation', layout=createDeck())
    
    while True:
        event, values = wCreateDeck.Read()
        if event in [None, 'Exit', 'Back']:
            break
        
        # Show/hide the 'auto deck' section based on radio buttons
        wCreateDeck['-AUTO-'].update(visible=values['-autoCheck-'])
        wCreateDeck['-EMPTY-'].update(visible=values['-emptyCheck-'])

        if event == 'Create Deck':
            # Check whether the deck name exists
            deckName = values['deckName'] + '.txt'
            deckFolder = Options.deck_folder_path()
            if deckName not in os.listdir(deckFolder):
                
                # Create a deck and fill it with cards if auto is checked
                if values['-autoCheck-'] == False or values['-source-'] != '':
                    cc.createDeck(values['-autoCheck-'], deckName, values['newLimit'], values['reviewLimit'], values['-source-'], values['-comp-'])
                    break
                
                # Inform the user if they have not selected a source for the auto deck
                elif values['-source-'] == '':
                    wCreateDeck.Element('-statusBar-').Update(status[2])
            
            # If the deck name is taken, then skip deck creation and inform user     
            else:
                wCreateDeck.Element('-statusBar-').Update(status[1] + deckName.replace('.txt', ''))

    wCreateDeck.Close()
    
    return


if __name__ == '__main__':
    createUI()
