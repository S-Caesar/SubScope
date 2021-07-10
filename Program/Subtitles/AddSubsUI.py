# -*- coding: utf-8 -*-

# UI for adding subtitle files to the user files

import PySimpleGUI as sg

def addScreen():
    text = [[sg.Text('placeholder window')]]

    addScreen = [[sg.Column(text)]]

    return addScreen


def addSubs():
    wAddScreen = sg.Window('Add Subtitles', layout=addScreen())
    
    while True:
        event, values = wAddScreen.read()
        
        if event == None or event == 'Exit':
            break

    return