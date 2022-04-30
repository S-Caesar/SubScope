# -*- coding: utf-8 -*-

from Program.Main import MainMenu as mm
from Program.Main import Initialise as init

def main():

    # Show the progress of initialisation
    initialise = init.Initialise()
    initialise.show()
    
    # Show the main menu
    mainMenu = mm.MainMenu()
    mainMenu.show()
    
if __name__ == '__main__':
    main()