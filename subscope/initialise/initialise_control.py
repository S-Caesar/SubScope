import threading
from enum import Enum

from subscope.initialise.initialise_state import InitialiseState
from subscope.initialise.initialise_view import InitialiseView
from subscope.nav import Nav
from subscope.settings.settings import Settings
from subscope.database.database import Database


class InitialiseControl:
    _NOT_STARTED = "Not Started"
    _IN_PROGRESS = "In Progress"
    _COMPLETE = "Complete"

    def __init__(self):
        self._state = InitialiseState(
            theme=Settings.main_theme(),
            initialisation_progress=self._NOT_STARTED,
            initialisation_steps=InitialisationSteps
        )
        self._view = InitialiseView(
            state=self._state
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break

            else:
                self._check_and_run_initialisation()
                self._handle(event)

        return Nav.MAIN_MENU

    def _handle(self, event):
        pass

    def _check_and_run_initialisation(self):
        if self._state.initialisation_progress == self._NOT_STARTED:
            self._state.initialisation_progress = self._IN_PROGRESS
            self._view.refresh_ui(self._state)
            threading.Thread(target=self._initialise).start()
        elif self._state.initialisation_progress == self._COMPLETE:
            self._view.close()

    def _initialise(self):
        self._check_or_create_settings_file()
        self._check_or_create_database()
        self._state.initialisation_progress = self._COMPLETE
        self._view.refresh_ui(self._state)

    def _check_or_create_settings_file(self):
        Settings.main_options()
        self._state.initialisation_steps.CHECK_SETTINGS.complete = True
        self._view.refresh_ui(self._state)

    def _check_or_create_database(self):
        Database.create_database()
        self._state.initialisation_steps.CHECK_DATABASE.complete = True
        self._view.refresh_ui(self._state)


class InitialisationSteps(Enum):
    CHECK_SETTINGS = ("Checking settings file", "-CHECK_SETTINGS-", False)
    CHECK_DATABASE = ("Checking database", "-CHECK_DATABASE-", False)

    def __init__(self, display_text, key, complete):
        self.display_text = display_text
        self.key = key
        self.complete = complete
