# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os


class HelpView:
    
    _PATH = os.path.dirname(os.path.realpath(__file__))
    _NAME = 'Help'
    
    @property
    def _layout(self):
        layout = [[sg.Column(self._setupLayout),
                   sg.Column(self._addSubsLayout)],
                  [sg.Text('')],
                  [sg.Button('Back')]]
        return layout
    
    @property
    def _setupLayout(self):
        text = [[sg.Text('To analyse the subtitle files, the sentences must first be \nparsed into individual words.')],
                [sg.Text('Navigate to the \'Setup\' file, and open \'Ichiran Setup.txt\'.')],
                [sg.Text('Follow the instructions in this file to set up the Ichiran parser. \nThis only needs to be done once.')],
                [sg.Image(self._PATH + '/setup_1.png')]]

        return [[sg.Column(text)]]
    
    @property
    def _addSubsLayout(self):
        text = [[sg.Text('Navigate to the \'Subtitles\' file, and create a folder for the content')],
                [sg.Image(self._PATH + '/addSubs_1.png')],
                [sg.Text('')],
                [sg.Text('Move the video files (.mp4 or .mkv) and subtitle files (.srt) to the folder')],
                [sg.Image(self._PATH + '/addSubs_2.png')],
                [sg.Text('')],
                [sg.Text('Make sure the matching video and subtitle files have the same name')],
                [sg.Image(self._PATH + '/addSubs_3.png')]]
    
        return [[sg.Column(text)]]
    
    
    @property
    def _window(self):
        window = sg.Window(self._name, layout=self._layout)
        return window
    
    
    def show(self):
        window = self._window
        while True:
            event, values = window.Read()
            if event in [None, 'Back']:
                window.Close()
                break