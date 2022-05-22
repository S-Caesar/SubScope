# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import pandas as pd

from subscope.package.Processing import CardCreation as cc
from subscope.package.database.database import Database as db
from subscope.package.Options import ManageOptions as mo
from subscope.package.Parsing.analysis_view import AnalysisView


def addCard(deckName, sortOptions, wordSources, database):
    # TODO: sort the table out to show POS, definition, etc, in separate columns

    headings = [[sg.Text('Selected Deck:'),
                 sg.Text(deckName)]]
    
    sorting = [[sg.Text('Sort words by:'),
                sg.Combo(sortOptions, size=(20,4), enable_events=False, key='-SORT-')]]
    
    search = [[sg.Text('Start typing to find words in the database:'),
               sg.In(size=(35,0), key='-REFINE-'),
               sg.Button('Refresh')]]
    
    sources = [[sg.Text('Select sources for cards:')],
              *[[sg.Checkbox(wordSources[i], key=f'wordSources {i}', enable_events=True, default=True)] for i in range(len(wordSources))]]
    
    # If there is data, show the database, otherwise direct the user to subtitle analysis
    data = database.values.tolist()
    if len(data) != 0:
        headers = list(database.columns)
        dataSearch = [[sg.Table(values=data, headings=headers, num_rows=15, enable_events=True)],
                      [sg.Button('Add Cards')]]        
    else:
        dataSearch = [[sg.Text('The database is empty.\nAnalyse subtitles to add words to it.', size=(100,2))],
                      [sg.Button('Analyse Subtitles')]]
    
    addCard = [[sg.Column(headings)],
                      
                [sg.Column(sorting),
                 sg.Column(search)],
                      
                [sg.Column(sources, size=(170,300), scrollable=True, justification='Top'),
                 sg.Column(dataSearch, size=(1000,300))]]  

    return addCard


def addUI(deckName, wordSources):
    
    sortOptions = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']
    
    deckFolder = mo.getSetting('paths', 'Deck Folder')
    database = db.read_database()
    
    # Trim the database to just show the word info in the UI
    headings = list(database)
    dataHeadings = headings[:5]
    for heading in headings:
        if heading not in dataHeadings:
            del database[heading]
            
    
    
    # TODO: split up the gloss info into proper columns
    # TODO: Words, but very slowly...
    import ast

    for x in range(len(database['gloss'])):
        
        database['gloss'][x] = ast.literal_eval(database['gloss'][x])
        if len(database['gloss'][x]) > 1:
            database['gloss'][x] = database['gloss'][x][0]

        try:
            database['gloss'][x] = database['gloss'][x]['pos']
        except:
            database['gloss'][x] = database['gloss'][x][0]['pos']
    
    
    # Add cards to the selected deck. Show database, and allow selection.
    wAddCard = sg.Window('Add Cards', layout=addCard(deckName, sortOptions, wordSources, database))
    while True:
        event, values = wAddCard.Read()
        if event is None or event == 'Exit':
            break
        
        sourceSelect=[]
        for x in range(len(wordSources)):
            if values[f'wordSources {x}'] == True:
                sourceSelect.append(wordSources[x])
                
        if event == 'Analyse Subtitles':
            wAddCard.close()
            AnalysisView().show()
        
        # TODO: currently need to press the button twice to get the list to update
        if event == 'Refresh':
            
            refine = values['-REFINE-']
            sort = values['-SORT-']
            
            # TODO: allow searching in Japanese as well
            databaseRefined = database[database['gloss'].str.contains(refine)] 
            
            # TODO: expand the sort options
            if sort in sortOptions:
                if sort == '':
                    databaseRefined.sort_values(by=['text'], inplace=True, ignore_index=True)
                elif sort == 'Hiragana':
                    databaseRefined.sort_values(by=['kana'], inplace=True, ignore_index=True)
                elif sort == 'Alphabet':
                    databaseRefined.sort_values(by=['gloss'], inplace=True, ignore_index=True)
            
            # Update the database display based on user selections
            wAddCard.Close()
            wAddCard = sg.Window('Add Cards', layout=addCard(deckName, sortOptions, wordSources, databaseRefined))
            wAddCard.Read()
        
        if event == 'Add Cards':
            # Add cards currently highlighted in the table
            for x in values[0]:
                targetWord = database['text'][x]
                
                # Get card info, then create the media files
                cardInfo, wordLoc = cc.getCardInfo(targetWord, database)
                
                deck = pd.read_csv(deckFolder + '/' + deckName, sep='\t')
                if len(deck[deck['wordJapanese']==cardInfo[4]]) == 0:
                    cc.addCard(deckFolder, deckName, cardInfo, deck)
                    cc.createMedia(wordLoc)
                    print('Cards successfully added to deck.')
                else:
                    print('Card already exists in deck:', cardInfo[4])
            
    wAddCard.close()
    
    return


if __name__ == '__main__':
    
    import os
    
    sourceFolder = mo.getSetting('paths', 'Source Folder')
    wordSources = next(os.walk(sourceFolder))[1]    
    
    deckName = 'a.txt'
    
    addUI(deckName, wordSources)