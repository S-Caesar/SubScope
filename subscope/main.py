# -*- coding: utf-8 -*-

from package.main_view import MainView
from package.initialise.initialise_view import InitialiseView

def main():

    # Show the progress of initialisation
    initialise = InitialiseView()
    initialise.show()
    
    # Show the main menu
    main = MainView()
    main.show()
    
if __name__ == '__main__':
    main()