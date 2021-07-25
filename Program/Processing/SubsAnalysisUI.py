# -*- coding: utf-8 -*-

# UI screens for subtitle analysis
import os
import pandas as pd
import PySimpleGUI as sg

from Program.Parsing import IchiranParse as ip
from Program.Processing import ParsedAnalysis as pa
from Program.General import FileHandling as fh


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

def wAnalysis(fileList=[]): 
    
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '\\'.join(startPath) + '\\User Data\\Subtitles'
    
    # set up the subtitle analysis window
    folderColumn = [[sg.Text('Select a folder containing subtitle files to be analysed.')],
                    [sg.In(size=(37, 1), enable_events=True, key='-FOLDER-'),
                     sg.FolderBrowse(initial_folder=startPath)]]
    
    # set up the subtitle analysis window
    subtitleListColumn = [[sg.Text('Subtitle Files')],
                          *[[sg.Checkbox(fileList[i], default=True, key=f'-SUBTITLES_{i}-')] for i in range(len(fileList))]]
    
    statisticsColumn = [[sg.Text('Statistics')],
                        [sg.Text('Select files in the left window to analyse')],
                        
                        [sg.Text('Comprehension:'),
                         sg.In(default_text=70, size=(3, 1), enable_events=True, key='-COMP-'), # input for desired comprehension score
                         sg.Text('%'),
                         sg.Button('Update Statistics')],
                        
                        *[[sg.Text(statsKeys[0][i]), 
                           sg.Text(size=(10,1), key=statsKeys[1][i])] for i in range(len(statsKeys[0]))]]
    
    subtitleButtons = [[sg.Button('Select All'),
                        sg.Button('Deselect All'),
                        sg.Button('Back')]]
    
    wAnalysis = [[sg.Column(folderColumn, size=(335,60))],
                 [sg.Column(subtitleListColumn, size=(300,300), scrollable=True),
                  sg.VSeperator(),
                  sg.Column(statisticsColumn)],
               
                 [sg.Column(subtitleButtons)]]
    
    return wAnalysis


def displayStats(window, stats):
    # Update each of the stats lines in the UI                
    for x in range(len(statsKeys[0])):
        window.Element(statsKeys[1][x]).Update(value=stats[x])
    return


def analysis():
    uAnalysis = sg.Window('Folder Selection', layout=wAnalysis())
    
    # Start UI loop
    while True:
        event, values = uAnalysis.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break

        if event == '-FOLDER-' and values['-FOLDER-'] != '':
            folder = values['-FOLDER-']
            fileList = fh.getFiles(folder, '.srt')
            
            # Update the window with the contents of the selected folder
            uAnalysis.Close()
            uAnalysis = sg.Window('File Analysis', layout=wAnalysis(fileList))       
            event, values = uAnalysis.Read()             

        statusDict = {'Select All': True, 'Deselect All': False}
        if event in statusDict and fileList != []:
            fileStatus = statusDict[event]
            for i in range(len(fileList)):
                uAnalysis.Element(f'-SUBTITLES_{i}-').Update(value=fileStatus)
                
        if event == 'Update Statistics':
            # Only analyse files if they are selected
            fnamesSelect = []
            for i in range(len(fileList)):
                if values[f'-SUBTITLES_{i}-'] == True:
                    fnamesSelect.append(fileList[i])
            
            if fnamesSelect == []:
                print('No files have been selected.')
            else:
                ip.parseWrapper(folder, fnamesSelect, os.listdir(folder))
                
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
                
                if values['-COMP-'] == '':
                    print('Invalid comprehension. Using default value of 70.')
                    comp = 70
                else:
                    comp = int(values['-COMP-'])

                uAnalysis.Element('-COMP-').update(value=comp)
                    
                stats = pa.prepStats(outputTable, 1, '==',  comp)
                displayStats(uAnalysis, stats)
                    
    uAnalysis.Close()
    return