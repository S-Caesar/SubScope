# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import pandas as pd

from Program.Parsing import IchiranParse as ip

def importScreen(path, deckHeadings, words):
    
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
               [sg.Table([words], def_col_width=8, auto_size_columns=False, key='-PREVIEW-', size=(0,18))]]
    
    importScreen = [[sg.Column(settings),
                     sg.VSeparator(),
                     sg.Column(preview, vertical_alignment='t')]]
    
    return importScreen


def importKnown():
    path = ''
    words = ['1', '2', '3', '4', '5', '6', '7', '8']
    deckHeadings = ['words']
    wImport = sg.Window('Import Known Words', layout=importScreen(path, deckHeadings, words))
    
    # Start UI loop
    while True:
        event, values = wImport.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break

        if event == '-PATH-':
            path = values['-PATH-']
            deck = open(path).read().split('\n')
            for x in range(len(deck)):
                deck[x] = deck[x].split('\t')

            deckHeadings = deck[0:1][0]
            
            # Update the combo list
            wImport.Element('-HEADINGS-').update(values=deckHeadings)
            # Update the default value
            wImport.Element('-HEADINGS-').update(deckHeadings[0])

        if event == 'Refresh List':
            index = deckHeadings.index(values['-HEADINGS-'])
            
            words = []
            for x in range(len(deck)):
                words.append(deck[x][index])
            
            if values['-WORD-'] != True:
                # Selected column is sentences, so parse them first
                sentences = ip.prepParseInput(words)
                
                fullTable = pd.DataFrame()
                for x in range(10):
                    parsedWords = ip.ichiranParse(sentences[x])
                    fullTable = fullTable.append(ip.flattenIchiran(parsedWords), ignore_index=True)
                
                words = fullTable['text'].tolist()
                
            
            # Split the words list in columns, then display
            displayWords = [words[x:x+8] for x in range(0, len(words), 8)]
            wImport.Element('-PREVIEW-').update(displayWords)
                    


        if event == 'Mark Words As Known':
            if values['-WORD-'] != True:
                # Parse the sentences to words
                fullTable = pd.DataFrame()
                #for x in range(len(sentences)):
                for x in range(len(5)):
                    parsedWords = ip.ichiranParse(sentences[x])
                    fullTable = fullTable.append(ip.flattenIchiran(parsedWords), ignore_index=True)
                
                words = fullTable['text'].tolist()
                
            # Remove duplicates
            words = list(dict.fromkeys(words))

            # Mark the words as known in the main database
            print('yep')
        
      
    wImport.Close()
    return

importKnown()