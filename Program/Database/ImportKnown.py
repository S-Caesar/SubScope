# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import pandas as pd
import timeit

from Program.Parsing import IchiranParse as ip
from Program.Database import DataHandling as dh

def importScreen(path, deckHeadings, tableHeadings, words):
    
    settings = [[sg.Text('Import known words from a text file (e.g. exported Anki deck)')],
                    
               [sg.Text('Select the file to be imported (*.txt):', size=(28,1)),
               sg.In(default_text=path, size=(20, 1), enable_events=True, key='-PATH-'),
                sg.FileBrowse(file_types=(('Text Files (*.txt)', '*.txt'),))],
               
               [sg.Text('Select the import column type:', size=(28,1)),
                sg.Radio('Word', 1, default=True, key='-WORD-'),
                sg.Radio('Sentence', 1, key='-SENTENCE-')],
               
               [sg.Text('Select the target column:', size=(28,1)),
                sg.Combo(deckHeadings, size=(15,1), key='-HEADINGS-'),
                sg.Button('Refresh List')],
               
               [sg.Text('Does the deck contain a header row?  '),
                sg.Radio('Yes', 2, default=True, key='-H_YES-'),
                sg.Radio('No', 2, key='-H_NO-')],
                    
               [sg.Text("=" * 55)],
               
               [sg.Text('Note:')],
               [sg.Text('- By default ALL words in the selected column will be marked as known.')],
               [sg.Text('- Sentences will be parsed to separate words. There is likely to be some \n  inaccuracy in marked words.')],
               [sg.Text('- Only a subset of parsed words will be display as this takes a long time.\n  when marking the words as learned, all sentences will be parsed.')],
               [sg.Text('- Words / sentences must not include furigana.')],
               
               [sg.Text("=" * 55)],
               
               [sg.Button('Back'),
                sg.Button('Mark Words As Known')]]
    
    preview = [[sg.Text('Word list preview:')],
               [sg.Table([words], headings=tableHeadings, def_col_width=8, auto_size_columns=False, key='-PREVIEW-', size=(0,18))]]
    
    importScreen = [[sg.Column(settings),
                     sg.VSeparator(),
                     sg.Column(preview, vertical_alignment='t')]]
    
    return importScreen


def importKnown(mainOptions):
    path = ''
    deck = ''
    tableHeadings = ['1', '2', '3', '4', '5', '6', '7', '8']
    words = ['', '', '', '', '', '', '', '']
    deckHeadings = ['']
    wImport = sg.Window('Import Known Words', layout=importScreen(path, deckHeadings, tableHeadings, words))
    
    # Start UI loop
    while True:
        event, values = wImport.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break

        if event == '-PATH-':
            path = values['-PATH-']
            if path != '':
                deck = open(path).read().split('\n')
                for x in range(len(deck)):
                    deck[x] = deck[x].split('\t')
    
                deckHeadings = deck[0:1][0]
                
                # Update the combo list
                wImport.Element('-HEADINGS-').update(values=deckHeadings)
                # Update the default value
                wImport.Element('-HEADINGS-').update(deckHeadings[0])

        if event == 'Refresh List':
            if values['-HEADINGS-'] != '' or deck != '':
                index = deckHeadings.index(values['-HEADINGS-'])

                words = []
                for x in range(len(deck)):
                    # Skip the header row if there is one
                    if x == 0 and values['-H_YES-'] == True:
                        continue
                    # Only append if the line isn't blank
                    elif deck[x] != ['']:
                        words.append(deck[x][index])
                
                if values['-WORD-'] != True:
                    # Selected column is sentences, so parse them first
                    sentences = ip.prepParseInput(words)
                    
                    fullTable = pd.DataFrame(columns=['text'])
                    # Just an example subset displayed because of how long parsing takes
                    for x in range(10):
                        if sentences[x] != '':
                            parsedWords = ip.ichiranParse(sentences[x])
                            fullTable = fullTable.append(ip.flattenIchiran(parsedWords), ignore_index=True)
                    
                    if len(words) != 0:
                        words = fullTable['text'].tolist()
                    
                # Split the words list in columns, then display
                displayWords = [words[x:x+8] for x in range(0, len(words), 8)]
                wImport.Element('-PREVIEW-').update(displayWords)
                    

        if event == 'Mark Words As Known':
            if values['-WORD-'] != True:
                index = deckHeadings.index(values['-HEADINGS-'])
                
                words = []
                for x in range(len(deck)):
                    words.append(deck[x][index])
                
                sentences = ip.prepParseInput(words)
                
                i=0
                j=0
                startTime = timeit.default_timer()
                # Parse the sentences to words
                fullTable = pd.DataFrame(columns=['text'])
                for x in range(len(sentences)):
                    if sentences[x] != '':
                        parsedWords = ip.ichiranParse(sentences[x])
                        fullTable = fullTable.append(ip.flattenIchiran(parsedWords), ignore_index=True)
                    
                    if i >= 20:
                        passedTime = timeit.default_timer() - startTime
                        estTime = round((passedTime / j) * (len(sentences)-j) / 60, 1)
                        
                        print('===================================')
                        print('Rows Complete:', x, '/', len(sentences))
                        print('Estimated time remaining:', estTime, 'minutes')
                        print('===================================')
                        
                        i=0
                    i+=1
                    j+=1
                    
                if len(words) != 0:
                    words = fullTable['text'].tolist()
                
            # Remove duplicates
            words = list(dict.fromkeys(words))

            # Mark the words as known in the main database
            databasePath = mainOptions['Default Paths']['Source Folder']
            
            dh.consolidateDatabase(databasePath, '', True, True)
            database = pd.read_csv(databasePath + '\\' + 'mainDatabase.txt', sep='\t')
            
            for x in range(len(words)):
                index = database.loc[database['text']==words[x]].index
                database.loc[database.index[index], 'status'] = 1
            
            database.to_csv(r'' + databasePath + '\\' + 'mainDatabase.txt', index=None, sep='\t', mode='w')
        
    wImport.Close()
    return


'''
'----------------------------------------------------------------------------'
from Program.Options import ManageOptions as mo
optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/mainOptions.txt'
mainOptions = mo.readOptions(optionsPath)
importKnown(mainOptions)
'----------------------------------------------------------------------------'
'''