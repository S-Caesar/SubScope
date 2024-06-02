import copy

from subscope.import_known.import_events import ImportEvents
from subscope.import_known.import_state import ImportState
from subscope.import_known.import_view import ImportView
from subscope.settings.settings import Settings


class ImportControl:
    def __init__(self):
        self._state = ImportState(
            theme=Settings.main_theme()
        )
        self._view = ImportView(
            state=copy.copy(self._state)
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break

            elif event.name == ImportEvents.Pass.name:
                pass

            elif event.name == ImportEvents.Navigate.name:
                self._view.close()
                return event.destination

            elif event.name is ImportEvents.UpdateState.name:
                self._state = event.state

            else:
                self._handle(event)

    def _handle(self, event):
        pass
