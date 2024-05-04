# -*- coding: utf-8 -*-

from subscope.main_view import MainView
from subscope.initialise.initialise_view import InitialiseView


def main():

    # Show the progress of initialisation
    initialise = InitialiseView()
    initialise.show()
    
    # Show the main menu
    main_view = MainView()
    main_view.show()


if __name__ == '__main__':
    main()
