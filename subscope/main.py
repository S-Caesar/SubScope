from subscope.initialise.initialise_control import InitialiseControl
from subscope.main_menu.main_control import MainControl
from subscope.nav import Nav


def main():
    destinations = {
        Nav.INITIALISE: InitialiseControl(),
        Nav.MAIN_MENU: MainControl(),
        Nav.RETIME: None,
        Nav.ANALYSE: None,
        Nav.IMPORT: None,
        Nav.DECKS: None,
        Nav.REVIEW: None,
        Nav.OPTIONS: None,
        Nav.SETUP: None
    }

    nav_target = Nav.INITIALISE
    while True:
        if nav_target is None:
            break
        else:
            print(f"Destination: {nav_target}")
            controller = destinations[nav_target]
            nav_target = controller.run()


if __name__ == "__main__":
    main()
