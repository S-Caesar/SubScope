import copy
import os
import re
import threading

import time

from subscope.analyse.ichiran import Ichiran
from subscope.analyse.parse_file import ParseFile
from subscope.analyse.stats import Stats
from subscope.analyse.analyse_events import AnalyseEvents
from subscope.analyse.analyse_state import AnalyseState
from subscope.analyse.analyse_view import AnalyseView
from subscope.settings.settings import Settings
from subscope.shared.sep import Sep


class AnalyseControl:
    _WHITELIST = re.compile("[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]", re.UNICODE)
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
                args=[event.selected_files, self._state.stats, event.detect_names]
            ).start()

    def _analyse_subtitle_files(self, input_filenames, stats, detect_names=False):
        start_time = time.time()
        output_folder = self._get_or_create_output_folder()

        character_names = []
        if detect_names:
            self._view.write_event(AnalyseEvents.UpdateDisplayMessage("Detecting names. This may take a minute or so."))
            character_names = self._find_character_names(self._state.input_folder, input_filenames)

        files_complete = f"Files Complete: {0} / {len(input_filenames)}"
        self._view.write_event(AnalyseEvents.UpdateDisplayMessage(f"{files_complete}"))
        for file_no, input_filename in enumerate(input_filenames):
            ParseFile(input_filename, self._state.input_folder, output_folder, character_names)
            self._update_parsing_progress(start_time, file_no, input_filenames)
        stats.analyse(output_folder, input_filenames)
        self._view.write_event(AnalyseEvents.UpdateStatsDisplay(stats))

    def _find_character_names(self, input_folder, input_filenames):
        # TODO works fairly well in a general sense, but will miss any brackets later in the sentence
        #  Not sure at the moment how to identify when the later brackets need to be taken, and how much of the
        #  preceding characters are covered by the brackets
        # Names can be found by looking for brackets at the start of a line, indicating someone speaking off-screen, or
        # nested brackets indicating a character introduction
        outer_bracket_open = "（"
        outer_bracket_close = "）"
        inner_bracket_open = "("
        inner_bracket_close = ")"
        full_names = []
        partial_names = []
        character_names = []
        for input_filename in input_filenames:
            input_filepath = os.path.join(input_folder, input_filename)
            lines = open(input_filepath, "r", encoding="utf8").read().split(Sep.NEW_LINE)
            lines = [line for line in lines if line != ""]
            for line in lines:
                if line[0] == outer_bracket_open:
                    if inner_bracket_open in line:
                        outer_open = line.find(outer_bracket_open)
                        outer_close = line.find(outer_bracket_close)
                        inner_open = line.find(inner_bracket_open)
                        inner_close = line.find(inner_bracket_close)
                        if inner_open < outer_close:
                            # Full character name introduction
                            family_or_full_name = line[outer_open + 1: inner_open]
                            given_name = line[inner_close + 1: outer_close]
                            full_name = family_or_full_name + given_name
                            if full_name not in character_names:
                                full_names.append(full_name)
                                character_names.append(full_name)
                        else:
                            # Otherwise, it's a second set of brackets, possibly the pronunciation foran English word
                            pass
                    elif line[-1] != outer_bracket_close:
                        # Off-screen character talking
                        name = line[line.find(outer_bracket_open) + 1:line.find(outer_bracket_close)]
                        if name not in character_names:
                            partial_names.append(name)
                            character_names.append(name)
                    else:
                        # Likely subtitles for text shown on in the show
                        pass

        removed = []
        for idx, name in enumerate(character_names):
            # See if any chars are not in the whitelist (indicating it is a generic identification of someone talking)
            checked_name = [char for char in name if self._WHITELIST.search(char)]
            checked_name = "".join(checked_name)
            if name != checked_name:
                character_names[idx] = ""

            # Attempt to tokenize the names. If it tried to split them up, they are likely to be names, or long text
            # of off-screen sounds, which hopefully won't turn up in the actual subtitle text as an exact match
            parse_attempt = Ichiran.parse_line(name)
            if len(parse_attempt[0][0][0]) == 1:
                removed.append(character_names[idx])
                character_names[idx] = ""

        character_names = [name for name in character_names if name != ""]
        return character_names

    def _get_or_create_output_folder(self):
        output_folder = os.path.join(self._state.input_folder, self._ANALYSED_OUTPUT_FOLDER_NAME)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        return output_folder

    def _update_parsing_progress(self, start_time, file_no, input_filenames):
        passed_time = time.time() - start_time
        est_time = round((passed_time / (file_no + 1)) * (len(input_filenames) - file_no + 1) / 60, 1)
        files_complete = f"Files Complete: {file_no + 1} / {len(input_filenames)}"
        time_remaining = f"Estimated time remaining: {est_time} minutes"
        self._view.write_event(AnalyseEvents.UpdateDisplayMessage(f"{files_complete}\n{time_remaining}"))
