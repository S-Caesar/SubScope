from subscope.analyse.analyse_control import AnalyseControl
from subscope.import_known.import_control import ImportControl
from subscope.initialise.initialise_control import InitialiseControl
from subscope.main_menu.main_control import MainControl
from subscope.nav import Nav
from subscope.retime.retime_control import RetimeControl


def main():
    destinations = {
        Nav.INITIALISE: InitialiseControl,
        Nav.MAIN_MENU: MainControl,
        Nav.RETIME: RetimeControl,
        Nav.ANALYSE: AnalyseControl,
        Nav.IMPORT: ImportControl,
        Nav.DECKS: None,
        Nav.REVIEW: None,
        Nav.SETTINGS: None,
        Nav.HELP: None
    }

    nav_target = Nav.INITIALISE
    while True:
        print(f"Destination: {nav_target}")
        if nav_target is None:
            break
        else:
            controller = destinations[nav_target]
            nav_target = controller().run()


if __name__ == "__main__":
    main()
