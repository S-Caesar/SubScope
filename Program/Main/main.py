# -*- coding: utf-8 -*-

from Program.Main import MainMenu as mm
from Program.Main import Initialise as init

def main():

    initialise = init.Initialise()
    initialise.show()
    
    mainMenu = mm.MainMenu()
    mainMenu.show()
    
    
if __name__ == '__main__':
    main()