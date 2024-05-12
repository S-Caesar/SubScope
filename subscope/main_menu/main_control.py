from subscope.main_menu.main_events import MainEvents
from subscope.main_menu.main_state import MainState
from subscope.main_menu.main_view import MainView
from subscope.settings.settings import Settings


class MainControl:

    def __init__(self):
        self._state = MainState(
            theme=Settings.main_theme()
        )
        self._view = MainView(
            state=self._state
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break

            elif event.name == MainEvents.Navigate.name:
                self._view.close()
                return event.destination

            else:
                self._handle(event)

    def _handle(self, event):
        pass
