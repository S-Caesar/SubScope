# -*- coding: utf-8 -*-

# UI screens for subtitle analysis
import os
import pandas as pd
import PySimpleGUI as sg

from Program.Parsing import IchiranParse as ip
from Program.Parsing import ParsedAnalysis as pa
from Program.General import FileHandling as fh
from Program.Database import DataHandling as dh


completedFiles = 0
totalFiles = 0
analysisTime = 0

status = ['Press \'Browse\' to select a location \nwith subtitles for analysis',
          'Press \'Analyse Files\' once subtitle \nfiles are selected on the left',
          ('Analysing file ', completedFiles, ' / ', totalFiles, '(Approximately ', analysisTime, 'minutes remaining)'),
          'Updating the database',
          'All selected files analysed']

statsDisplay = [['Number:'              + ' '*22, 
                 'Unknown:'             + ' '*20, 
                 'Comprehension (%):'   + ' '*4, 
                 'Number:'              + ' '*22, 
                 'Unknown:'             + ' '*20],
                ['-',        '-',          '-',      '-',        '-'         ],
                ['-aWORDS-', '-aUNKNOWN-', '-COMP-', '-uWORDS-', '-uUNKNOWN-']]


def wAnalysis(status, fileList=[]): 
    
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '/'.join(startPath) + '/User Data/Subtitles'
    
    folderColumn = [[sg.Text('Select a folder containing subtitle files to be analysed.')],
                    [sg.In(size=(37, 1), enable_events=True, key='-FOLDER-'),
                     sg.FolderBrowse(initial_folder=startPath)]]
    
    subtitleListColumn = [[sg.Text('Subtitle Files', font=('any', 10, 'bold'))],
                          *[[sg.Checkbox(fileList[i], default=True, key=f'-SUBTITLES_{i}-')] for i in range(len(fileList))]]
    
    statisticsColumn = [[sg.Button('Analyse Files')],
                        [sg.Text('')],
                        [sg.Text('Status', font=('any', 10, 'bold'))],
                        [sg.Text(status, size=(30,2), key='-STATUS-')],
                        [sg.Text('')],
                        
                        [sg.Text('All Words', font=('any', 10, 'bold'))],
                        *[[sg.Text(statsDisplay[0][i] + str(statsDisplay[1][i]), size=(30, 1), key=statsDisplay[2][i])] for i in range(0,3)],
                        [sg.Text('')],
                        
                        [sg.Text('Unique Words', font=('any', 10, 'bold'))],
                        *[[sg.Text(statsDisplay[0][i] + str(statsDisplay[1][i]), size=(30, 1), key=statsDisplay[2][i])] for i in range(3,5)]]    
    
    subtitleButtons = [[sg.Button('Select All'),
                        sg.Button('Deselect All'),
                        sg.Button('Back')]]
    
    wAnalysis = [[sg.Column(folderColumn, size=(335,60))],
                 [sg.Column(subtitleListColumn, size=(300,300), scrollable=True),
                  sg.VSeperator(),
                  sg.Column(statisticsColumn)],
               
                 [sg.Column(subtitleButtons)]]
    
    return wAnalysis


def analysis():
    uAnalysis = sg.Window('Folder Selection', layout=wAnalysis(status[0]))
    
    while True:
        event, values = uAnalysis.Read()
        if event is None or event == 'Exit':
            break
        
        # TODO: this only seems to run the first time a folder is selected
        if event == '-FOLDER-' and values['-FOLDER-'] != '':
            folder = values['-FOLDER-']

            # TODO: add support for other file types
            fileList = fh.getFiles(folder, '.srt')
            
            # Update the window with the contents of the selected folder
            uAnalysis.Close()
            uAnalysis = sg.Window('File Analysis', layout=wAnalysis(status[1], fileList))       
            event, values = uAnalysis.Read()             

        statusDict = {'Select All': True, 'Deselect All': False}
        if event in statusDict and fileList != []:
            fileStatus = statusDict[event]
            for i in range(len(fileList)):
                uAnalysis.Element(f'-SUBTITLES_{i}-').Update(value=fileStatus)
                
        if event == 'Analyse Files':
            # Only analyse files if they are selected
            fnamesSelect = []
            for i in range(len(fileList)):
                if values[f'-SUBTITLES_{i}-'] == True:
                    fnamesSelect.append(fileList[i])
            
            # TODO: add status readout to the UI
            if fnamesSelect != []:
                ip.parseWrapper(folder, fnamesSelect)
                
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
                    fullTable = pd.read_csv(folder + '/Text/' +  fnamesSelect[x], sep='\t')
                    outputTable = outputTable.append(fullTable)
                    
                outputTable = outputTable.reset_index(drop=True)
                    
                stats = pa.simpleAnalysis(outputTable)

                for x in range(len(statsDisplay[0])):
                    uAnalysis.Element(statsDisplay[2][x]).update(statsDisplay[0][x] + str(stats[x]))
                uAnalysis.Element('-STATUS-').update(status[4])
            
            # Update the database with the newly analysed content
            dh.databaseWrapper(write=True)
        
        # When the window is recreated with the selected files, the back button
        # has to be pressed twice unless I put the event trigger at the end
        if event == 'Back':
            break
                    
    uAnalysis.Close()
    return