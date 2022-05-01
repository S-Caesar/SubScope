# -*- coding: utf-8 -*-

# UI to guide users to install Ichiran

import PySimpleGUI as sg
import os

def setupScreen():
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '\\'.join(startPath) + '\\Program\\Subtitles\\'
       
    text = [[sg.Text('To analyse the subtitle files, the sentences must first be \nparsed into individual words.')],
            [sg.Text('Navigate to the \'Setup\' file, and open \'Ichiran Setup.txt\'.')],
            [sg.Text('Follow the instructions in this file to set up the Ichiran parser. \nThis only needs to be done once.')],
            [sg.Image(startPath + 'setup_1.png')],
            [sg.Text('')],
            [sg.Button('Back')]]

    initalSetup = [[sg.Column(text)]]

    return initalSetup


def initialSetup():
    wInitialSetup = sg.Window('Initial Setup', layout=setupScreen())
    
    while True:
        event, values = wInitialSetup.read()
        
        if event == None or event == 'Exit' or event == 'Back':
            break
        
    wInitialSetup.Close()

    return