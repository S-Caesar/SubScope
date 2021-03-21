# All layouts for the UserInterface

import PySimpleGUI as sg

def splashScreen():
    # set up the subtitle selection window
    splashScreen = [[sg.Text('Review / Modify SRS Cards')],
                    [sg.Button('Review Cards'),
                     sg.Button('Change Settings'),
                     sg.Button('Browse Database')],
                    [sg.Text("=" * 40)],
                   
                    [sg.Text('Select a folder containing subtitle files to be analysed.')],
                    [sg.In(size=(37, 1), enable_events=True, key="-FOLDER-"),
                     sg.FolderBrowse()]]
    
    return splashScreen
    
def settingsScreen(mainOptions, subOptions):
    mainOptions = [*[[sg.Text(mainOptions[i], enable_events=True, size=(200,1), key=f'-OPTIONS- {i}')] for i in range(len(mainOptions))],
                         [sg.Text(' ')],
                         [sg.Button('Back')]]
        
    subOptions = [[sg.Text(subOptions[i], size=(200,1), key=f'-SUBOPTIONS- {i}')] for i in range(len(subOptions))]
    
    settingsScreen = [[sg.Column(mainOptions, size=(100,300)),
                     sg.VSeparator(),
                     sg.Column(subOptions, size=(400,300))]]
    
    return settingsScreen
    
def databaseScreen():
    # Window for browsing the database - placeholder
    # TODO
    databaseNav = [[sg.Text('Placeholder Text')]]
    databaseScreen = [[sg.Column(databaseNav, size=(500,500))]]
    
    return databaseScreen

def subAnalysisWindow(fnames):
    # set up the subtitle analysis window
    subtitleListColumn = [[sg.Text('Subtitle Files')],
                          *[[sg.Checkbox(fnames[i], default=True, key=f"-SUBTITLES- {i}")] for i in range(len(fnames))]]
    
    statisticsColumn = [[sg.Text('Statistics')],
                        [sg.Text('Select files in the left window to analyse')],
                        
                        [sg.Text('Comprehension:'),
                         sg.In(size=(3, 1), enable_events=True, key="-COMP-"), # input for desired comprehension score
                         sg.Text('%'),
                         sg.Button('Update Statistics')],
                        
                        [sg.Text('Number of Unique Words: '),
                         sg.Text(size=(6,1), key='-NoUniqueWords-')],

                        [sg.Text('Number of Words Appearing Only Once: '),
                         sg.Text(size=(6,1), key='-NoOnlyOnce-')],
                        
                        [sg.Text('Number of Words Appearing Specified Times: '),
                         sg.Text(size=(6,1), key='-NoOnlyX-')],
                        
                        [sg.Text('Total Number of Words: '),
                         sg.Text(size=(6,1), key='-TotalWords-')],
                        
                        [sg.Text('Total Number of Unknown Words: '),
                         sg.Text(size=(6,1), key='-TotalUnknown-')],
                        
                        [sg.Text('Comprehension Score: '),
                         sg.Text(size=(6,1), key='-CompScore-'),
                         sg.Text('%')],
                        
                        [sg.Text('Words Required for Specified Comprehension: '),
                         sg.Text(size=(6,1), key='-CompWords-')],
                        
                        [sg.Text('Unknown Words Required for Specified Comprehension: '),
                         sg.Text(size=(6,1), key='-CompUnk-')]]
    
    databaseColumn = [[sg.Text('Database')],
                      [sg.Text('Record subtitle information to the database')],
                      
                      [sg.Text('Show Name'),
                       sg.In(size=(19, 1), enable_events=True, key="-showName-")],
                      
                      [sg.Text('Episode Number Format'),
                       sg.Radio('S00E00', 1, enable_events=True, key='-epFormat_S00E00-', default=True),
                       sg.Radio('000', 1, enable_events=True, key='-epFormat_000-')],
                      
                      [sg.Text('Delimeter'),
                       sg.Radio('.', 2, enable_events=True, key='-delimeter_1-', default=True),
                       sg.Radio(',', 2, enable_events=True, key='-delimeter_2-'),
                       sg.Radio('_', 2, enable_events=True, key='-delimeter_3-')],
                      
                      [sg.Button('Add To Database')]]
    
                        # TODO add the file metadata stuff - is this where I should use a class?
    
    subtitleButtons = [[sg.Button('Select All'),
                        sg.Button('Deselect All'),
                        sg.Button('Back')]]
    
    subAnalysisWindow = [[sg.Column(subtitleListColumn, size=(300,300), scrollable=True),
                          sg.VSeperator(),
                          sg.Column(statisticsColumn),
                          sg.VSeperator(),
                          sg.Column(databaseColumn)],
                        
                         [sg.Column(subtitleButtons)]]
    
    return subAnalysisWindow