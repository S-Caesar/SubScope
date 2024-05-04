from subscope.initialise.initialise_control import InitialiseControl
from subscope.main_view import MainView


def main():

    # Show the progress of initialisation
    controller = InitialiseControl()
    controller.run()
    
    # Show the main menu
    main_view = MainView()
    main_view.show()


if __name__ == '__main__':
    main()
