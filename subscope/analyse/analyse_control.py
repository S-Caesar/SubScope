import copy
import os
import threading

import time

from subscope.analyse.parse_file import ParseFile
from subscope.analyse.stats import Stats
from subscope.analyse.analyse_events import AnalyseEvents
from subscope.analyse.analyse_state import AnalyseState
from subscope.analyse.analyse_view import AnalyseView
from subscope.settings.settings import Settings


class AnalyseControl:
    _ANALYSED_OUTPUT_FOLDER_NAME = "text"

    def __init__(self):
        self._state = AnalyseState(
            theme=Settings.main_theme()
        )
        self._view = AnalyseView(
            state=copy.copy(self._state)
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break

            elif event.name == AnalyseEvents.Pass.name:
                pass

            elif event.name == AnalyseEvents.Navigate.name:
                self._view.close()
                return event.destination

            elif event.name is AnalyseEvents.UpdateState.name:
                self._state = event.state

            elif event.name == AnalyseEvents.ReopenWindow.name:
                self._view.close()
                self._view = AnalyseView(
                    state=self._state
                )

            else:
                self._handle(event)

    def _handle(self, event):
        if event.name == AnalyseEvents.AnalyseSubtitles.name:
            self._state.stats = Stats()
            threading.Thread(
                target=self._analyse_subtitle_files,
                args=[event.selected_files, self._state.stats]
            ).start()

    def _analyse_subtitle_files(self, input_filenames, stats):
        start_time = time.time()
        output_folder = self._get_or_create_output_folder()
        files_complete = f"Files Complete: {0} / {len(input_filenames)}"
        self._view.write_event(AnalyseEvents.UpdateDisplayMessage(f"{files_complete}"))
        for file_no, input_filename in enumerate(input_filenames):
            ParseFile(input_filename, self._state.input_folder, output_folder)
            passed_time = time.time() - start_time
            est_time = round((passed_time / (file_no + 1)) * (len(input_filenames) - file_no + 1) / 60, 1)
            files_complete = f"Files Complete: {file_no + 1} / {len(input_filenames)}"
            time_remaining = f"Estimated time remaining: {est_time} minutes"
            self._view.write_event(AnalyseEvents.UpdateDisplayMessage(f"{files_complete}\n{time_remaining}"))

        stats.analyse(output_folder, input_filenames)
        self._view.write_event(AnalyseEvents.UpdateStatsDisplay(stats))

    def _get_or_create_output_folder(self):
        output_folder = os.path.join(self._state.input_folder, self._ANALYSED_OUTPUT_FOLDER_NAME)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        return output_folder
