# -*- coding: utf-8 -*-

# UI screens for subtitle analysis
import os
import pandas as pd
import PySimpleGUI as sg

from Program.Parsing import IchiranParse as ip
from Program.Processing import ParsedAnalysis as pa

'------------------------------------------------------------------------'
statsKeys = [['Total Number of Words:',
              'Total Number of Unknown Words:',
              'Number of Unique Words:',
              'Number of Unique Unknown Words:',
              'Number of Unique Words in Dictionary Form:',
              'Number of Unique Unknown Words in Dictionary Form:',
              'The Number of Words of the Frequency Specified:',
              'Comprehension (%):',
              'Total Words for Specified Comprehension:',
              'Total Unknown Words for Specified Comprehension:'],
         
             ['-noWords-',
              '-noUnknown-',
              '-noUnique-',
              '-noUniqueUnk-',
              '-noUniqueDict-',
              '-noUniqueDictUnk-',
              '-noSpecFreq-',
              '-comprehension-',
              '-noInputComp-',
              '-noInputCompUnk-']]
'------------------------------------------------------------------------'

def subsAnalysisWindow(fnames): 
    # set up the subtitle analysis window
    subtitleListColumn = [[sg.Text('Subtitle Files')],
                          *[[sg.Checkbox(fnames[i], default=True, key=f"-SUBTITLES- {i}")] for i in range(len(fnames))]]
    
    statisticsColumn = [[sg.Text('Statistics')],
                        [sg.Text('Select files in the left window to analyse')],
                        
                        [sg.Text('Comprehension:'),
                         sg.In(default_text=70, size=(3, 1), enable_events=True, key="-COMP-"), # input for desired comprehension score
                         sg.Text('%'),
                         sg.Button('Update Statistics')],
                        
                        *[[sg.Text(statsKeys[0][i]), 
                           sg.Text(size=(10,1), key=statsKeys[1][i])] for i in range(len(statsKeys[0]))]]
    
    subtitleButtons = [[sg.Button('Select All'),
                        sg.Button('Deselect All'),
                        sg.Button('Back')]]
    
    subAnalysisWindow = [[sg.Column(subtitleListColumn, size=(300,300), scrollable=True),
                          sg.VSeperator(),
                          sg.Column(statisticsColumn)],
                        
                         [sg.Column(subtitleButtons)]]
    
    return subAnalysisWindow

def displayStats(window, stats):
    # Update each of the stats lines in the UI                
    for x in range(len(statsKeys[0])):
        window.Element(statsKeys[1][x]).Update(value=stats[x])
        
    return


def subsAnalysisUI(folder):
    # Get a list of files in folder
    try:
        file_list = os.listdir(folder)
    except:
        file_list = []

    fnames = [f for f in file_list
              if os.path.isfile(os.path.join(folder, f))
              and f.lower().endswith(('.srt'))
              or os.path.isfile(os.path.join(folder, f))
              and f.lower().endswith(('.ass'))]

    # initialise the subtitle analysis window
    wAnalysis = sg.Window('File Analysis').Layout(subsAnalysisWindow(fnames))

    while True:
        event, values = wAnalysis.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
        
        if event == 'Select All':
            for i in range(len(fnames)):
                wAnalysis.Element(f"-SUBTITLES- {i}").Update(value=True)
                
        if event == 'Deselect All':
            for i in range(len(fnames)):
                wAnalysis.Element(f"-SUBTITLES- {i}").Update(value=False)
                
        if event == "-COMP-":
            if values["-COMP-"] != '':
                comprehension = int(values["-COMP-"])
                
        if event == 'Update Statistics':
            # Only analyse files if they are selected
            fnamesSelect = []
            for i in range(len(fnames)):
                if values[f"-SUBTITLES- {i}"] == True:
                    fnamesSelect.append(fnames[i])
            
            if fnamesSelect == []:
                print('No files have been selected.')
            else:
                ip.parseWrapper(folder, fnamesSelect, file_list)
                
                # For every specified file, create a list containing the names of the analysed text files
                dataFiles = []
                for x in range(len(fnamesSelect)):
                    fnamesSelect[x] = fnamesSelect[x].split('.')
                    del fnamesSelect[x][-1]
                    fnamesSelect[x] = '.'.join(fnamesSelect[x])
                    fnamesSelect[x] = fnamesSelect[x] + '_full.txt'
                    dataFiles.append(fnamesSelect[x])
                
                # Read each of the files to be analysed and combine into a single table
                outputTable = pd.DataFrame()
                for x in range(len(fnamesSelect)):
                    fullTable = pd.read_csv(folder + '/' +  fnamesSelect[x], sep='\t')
                    outputTable = outputTable.append(fullTable)
                outputTable = outputTable.reset_index(drop=True)
                
                # Analyse the combined table and return the stats, then update the UI to display the results
                try:
                    comprehension = int(values['-COMP-'])
                except:
                    print('Invalid comprehension. Using default value of 70.')
                    comprehension = 70
                    wAnalysis.Element('-COMP-').update(value=comprehension)
                    
                
                stats = pa.prepStats(outputTable, 1, '==',  comprehension)
                displayStats(wAnalysis, stats)
            
    wAnalysis.Close()
    return