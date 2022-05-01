# -*- coding: utf-8 -*-

# UI for adding subtitle files to the user files

import PySimpleGUI as sg
import os

def addScreen():
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '\\'.join(startPath) + '\\Program\\Subtitles\\'
       
    text = [[sg.Text('Navigate to the \'Subtitles\' file, and create a folder for the content')],
            [sg.Image(startPath + 'addSubs_1.png')],
            [sg.Text('')],
            [sg.Text('Move the video files (.mp4 or .mkv) and subtitle files (.srt) to the folder')],
            [sg.Image(startPath + 'addSubs_2.png')],
            [sg.Text('')],
            [sg.Text('Make sure the matching video and subtitle files have the same name')],
            [sg.Image(startPath + 'addSubs_3.png')],
            [sg.Text('')],
            [sg.Button('Back')]]

    addScreen = [[sg.Column(text)]]

    return addScreen


def addSubs():
    wAddScreen = sg.Window('Add Subtitles', layout=addScreen())
    
    while True:
        event, values = wAddScreen.read()
        
        if event == None or event == 'Exit' or event == 'Back':
            break
        
    wAddScreen.Close()

    return