import copy
import os
import threading

import pandas as pd
import time

from subscope.analyse.parse_file import ParseFile
from subscope.analyse.stats import Stats
from subscope.analyse.analyse_events import AnalyseEvents
from subscope.analyse.analyse_state import AnalyseState
from subscope.analyse.analyse_view import AnalyseView
from subscope.settings.settings import Settings
from subscope.utilities.file_handling import FileHandling as fh
from subscope.database.database import Database as db


class AnalyseControl:
    _DATA_TABLE_SUFFIX = "_data_table"
    _ANALYSED_OUTPUT_FOLDER_NAME = "text"
    _TEXT_FILE_TYPE = ".txt"
    _TAB_SEPERATOR = "\t"

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

        output_data_table = self._read_data_table_files_to_dataframe(output_folder, input_filenames)
        self._analyse_data_table(output_data_table, stats)

    def _get_or_create_output_folder(self):
        output_folder = os.path.join(self._state.input_folder, self._ANALYSED_OUTPUT_FOLDER_NAME)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        return output_folder

    def _read_data_table_files_to_dataframe(self, output_folder, files):
        files = fh().rename_files(files, self._DATA_TABLE_SUFFIX, self._TEXT_FILE_TYPE)
        output_tables = []
        for file in files:
            if file in os.listdir(output_folder):
                filepath = os.path.join(output_folder, file)
                data_table = pd.read_csv(filepath, sep=self._TAB_SEPERATOR).fillna(0)
                output_tables.append(data_table)
        output_table = pd.concat(output_tables)
        return output_table

    def _analyse_data_table(self, output_table, stats):
        if not output_table.empty:
            output_table.reset_index(drop=True)
            self._analyse_words(output_table, stats)
            db.populate_database()

    def _analyse_words(self, data_table, stats):
        # Remove any words that don't have a definition
        data_table = data_table[data_table.gloss != 0]
        number_of_words = len(data_table)

        # Group duplicate rows, counting the number of occurrences, then sort descending by frequency
        unique_words = data_table.groupby(["text"]).size().reset_index()
        unique_words.rename(columns={0: "frequency"}, inplace=True)
        unique_words.sort_values(by=["frequency"], ascending=False, inplace=True)
        unique_words = unique_words.reset_index(drop=True)
        number_of_unique_words = len(unique_words)

        # Read the database and filter known words (status == 1)
        database = db.read_database()
        known_words = database.loc[database["status"] == 1]

        # Compare the known words from the database with the data_table
        unknown_words = self._dataframe_difference(data_table, known_words, "left_only", True)
        number_of_unknown_words = len(unknown_words)

        unknown_unique_words = self._dataframe_difference(unique_words, known_words, "left_only", True)
        number_of_unknown_unique_words = len(unknown_unique_words)

        comprehension = round(((number_of_words - number_of_unknown_words) / number_of_words) * 100)

        stats.total_words = number_of_words
        stats.total_unknown = number_of_unknown_words
        stats.comprehension = comprehension
        stats.total_unique = number_of_unique_words
        stats.unique_unknown = number_of_unknown_unique_words

        self._view.write_event(AnalyseEvents.UpdateStatsDisplay(stats))

    @staticmethod
    def _dataframe_difference(df_1, df_2, column=None, drop_merge=True):
        """
        Compare two DataFrames and return lines that only appear in df_1 (column='left_only'),
        df_2 (columns='right_only'), or both (columns='both')
        """
        comparison_table = df_1.merge(df_2, indicator=True, how='outer')
        if column in ["left_only", "right_only", "both"]:
            difference = comparison_table[comparison_table['_merge'] == column]
        else:
            raise Exception("Invalid value for column. Must be one of: 'left_only', 'right_only', 'both'")

        if drop_merge:
            difference = difference.reset_index(drop=True)
            del difference["_merge"]

        return difference
