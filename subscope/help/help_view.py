import PySimpleGUI as sg
import os


class HelpView:
    
    _PATH = os.path.dirname(os.path.realpath(__file__))
    _NAME = 'Help'
    
    @property
    def _layout(self):
        layout = [[sg.Column(self._setup_layout),
                   sg.Column(self._add_subs_layout)],
                  [sg.Text('')],
                  [sg.Button('Back')]]
        return layout
    
    @property
    def _setup_layout(self):
        text = [[sg.Text('To analyse the subtitle files, the sentences must first be \n'
                         'parsed into individual words.')],
                [sg.Text('Navigate to the \'Setup\' file, and open \'Ichiran Setup.txt\'.')],
                [sg.Text('Follow the instructions in this file to set up the Ichiran parser. \n'
                         'This only needs to be done once.')],
                [sg.Image(self._PATH + '/setup_1.png')]]

        return [[sg.Column(text)]]
    
    @property
    def _add_subs_layout(self):
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
        window = sg.Window(self._NAME, layout=self._layout)
        return window

    def show(self):
        window = self._window
        while True:
            event, values = window.Read()
            if event in [None, 'Back']:
                window.Close()
                break
