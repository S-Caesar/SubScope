# -*- coding: utf-8 -*-

# SubRetimer
# Change the subtitle timestamps if the video and subs are out of sync

import PySimpleGUI as sg
import math
import os

sg.theme('BlueMono')

def wSetup():
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '\\'.join(startPath) + '\\User Data\\Subtitles'
    
    # set up the subtitle analysis window
    folderColumn = [[sg.Text('Select a folder containing subtitle files to be retimed.')],
                    [sg.In(size=(37, 1), enable_events=True, key="-FOLDER-"),
                     sg.FolderBrowse(initial_folder=startPath)]]
    
    wSetup = [[sg.Column(folderColumn, size=(335,60))]]
                          
    return wSetup


def wSubRetimer(fnames): 
    # set up the subtitle analysis window
    subsColumn = [[sg.Text('Subtitle Files')],
                 *[[sg.Checkbox(fnames[i], default=True, key=f"-SUBTITLES- {i}")] for i in range(len(fnames))]]
    
    retimeColumn = [[sg.Text('Time offset:'),
                     sg.In(default_text='-2.0', size=(10, 1), enable_events=True, key='-OFFSET-'),
                     sg.Button('Update Files', enable_events=True)]]
    
    buttonsColumn = [[sg.Button('Select All', enable_events=True),
                      sg.Button('Deselect All', enable_events=True),
                      sg.Button('Back', enable_events=True)]]
    
    
    wSubRetimer = [[sg.Column(subsColumn, size=(300,300), scrollable=True),
                    sg.VSeperator(),
                    sg.Column(retimeColumn, size=(300,300))],
                   [sg.Column(buttonsColumn)]]
                          
    return wSubRetimer


def retime(folder, subFile, offset):

    inFile = open(folder + '/' + subFile, 'r', encoding="utf8").read()

    file = inFile.split('\n')
    
    for x in range(len(file)):
        if '-->' in file[x]:
            file[x] = file[x].split(' --> ')
            
            for y in range(len(file[x])):
                file[x][y] = file[x][y].split(':')
            
                # Convert to seconds and add offset
                time = float(file[x][y][0])*3600 + \
                       float(file[x][y][1])*60 + \
                       float(file[x][y][2].replace(',','.'))
                       
                time = time + offset    
                
                hours = math.floor(time/3600)
                mins = math.floor((time-(hours*3600))/60)
                secs = round((time-(hours*3600)-(mins*60)),3)
                secs = str(secs).split('.')
                
                if len(str(hours)) == 1:
                    hours = '0' + str(hours)
                    
                if len(str(mins)) == 1:
                    mins = '0' + str(mins)
                
                if len(str(secs[0])) == 1:
                    secs[0] = '0' + str(secs[0])
                
                if len(str(secs[1])) == 1:
                    secs[1] = str(secs[1]) + '00'
                elif len(str(secs[1])) == 2:
                    secs[1] = str(secs[1]) + '0'
                    
                secs = ','.join(secs)
                    
                time = [str(hours), str(mins), str(secs)]
                time = ':'.join(time)
                
                file[x][y] = time
                
            file[x] = ' --> '.join(file[x])

    file = '\n'.join(file)
    
    open(folder + '/' + subFile, 'w', encoding="utf8").write(file)
    
    return


