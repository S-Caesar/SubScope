import threading
from enum import Enum

from subscope.initialise.initialise_view import InitialiseView
from subscope.options.options import Options
from subscope.database.database import Database


class InitialiseControl:
    _NOT_STARTED = "Not Started"
    _IN_PROGRESS = "In Progress"
    _COMPLETE = "Complete"

    def __init__(self):
        self._initialisation_progress = InitialisationProgress
        self._initialisation_state = self._NOT_STARTED
        self._view = InitialiseView(
            theme=Options.main_theme(),
            initialisation_progress=self._initialisation_progress
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break
            else:
                self._handle(event)

            if self._initialisation_state == self._NOT_STARTED:
                self._initialisation_state = self._IN_PROGRESS
                threading.Thread(target=self._initialise).start()
            elif self._initialisation_state == self._COMPLETE:
                self._view.close()

    def _handle(self, event):
        pass

    def _initialise(self):
        self._initialise_packages()
        self._check_or_create_settings_file()
        self._check_or_create_database()
        self._initialisation_state = self._COMPLETE

    def _initialise_packages(self):
        # TODO not sure what I was originally intending for this to do, but it has never done anything
        self._initialisation_progress.INITIALISE_PACKAGES.complete = True
        self._view.update_progress(self._initialisation_progress)

    def _check_or_create_settings_file(self):
        Options.main_options()
        self._initialisation_progress.CHECK_SETTINGS.complete = True
        self._view.update_progress(self._initialisation_progress)

    def _check_or_create_database(self):
        Database.create_database()
        self._initialisation_progress.CHECK_DATABASE.complete = True
        self._view.update_progress(self._initialisation_progress)


class InitialisationProgress(Enum):
    INITIALISE_PACKAGES = ("Setting up packages", "-INITIALISE_PACKAGES-", False)
    CHECK_SETTINGS = ("Checking settings file", "-CHECK_SETTINGS-", False)
    CHECK_DATABASE = ("Checking database", "-CHECK_DATABASE-", False)

    def __init__(self, display_text, key, complete):
        self.display_text = display_text
        self.key = key
        self.complete = complete
