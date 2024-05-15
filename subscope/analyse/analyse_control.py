import copy
import os
import pandas as pd
import re
import time
from multiprocessing import Pool
import tqdm

from subscope.analyse.Stats import Stats
from subscope.analyse.analyse_events import AnalyseEvents
from subscope.analyse.analyse_state import AnalyseState
from subscope.analyse.analyse_view import AnalyseView
from subscope.settings.settings import Settings
from subscope.utilities.file_handling import FileHandling as fh
from subscope.analyse.ichiran import Ichiran
from subscope.database.database import Database as db


class AnalyseControl:
    _WHITELIST = re.compile("[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]", re.UNICODE)
    _DATA_TABLE_SUFFIX = "_data_table"
    _SUBS_ONLY_SUFFIX = "_subs_only"
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
            state = copy.copy(self._state)
            state.stats = self._analyse_subtitle_files(event.selected_files)
            self._view.write_event(AnalyseEvents.UpdateState(state))
            self._view.write_event(AnalyseEvents.UpdateStatsDisplay(state.stats))

    def _analyse_subtitle_files(self, files):
        output_folder = self._get_or_create_output_folder()
        self._analyse_files(self._state.folder, output_folder, files)
        output_data_table = self._read_data_table_files_to_dataframe(output_folder, files)
        stats = self._analyse_data_table(output_data_table)
        return stats

    def _get_or_create_output_folder(self):
        output_folder = os.path.join(self._state.folder, self._ANALYSED_OUTPUT_FOLDER_NAME)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        return output_folder

    def _read_data_table_files_to_dataframe(self, output_folder, files):
        output_table = pd.DataFrame()
        files = fh.rename_files(files, self._DATA_TABLE_SUFFIX, self._TEXT_FILE_TYPE)
        for file in files:
            if file in os.listdir(output_folder):
                filepath = os.path.join(output_folder, file)
                data_table = pd.read_csv(filepath, sep=self._TAB_SEPERATOR).fillna(0)
                output_table = output_table.append(data_table)
        return output_table

    def _analyse_data_table(self, output_table):
        stats = []
        if not output_table.empty:
            output_table.reset_index(drop=True)
            stats = self._analyse_words(output_table)

            # TODO: this will update all sources, not just analysed ones, so this needs improving
            # Update the database with the newly analysed content
            db.populate_database()
        return stats

    def _analyse_files(self, input_folder, output_folder, input_files):
        # TODO: currently stripping of text is based on .srt files; add support for other types (e.g. .ass)
        subs_only = fh.rename_files(input_files, '_subs_only', '.txt')
        data_table = fh.rename_files(input_files, '_data_table', '.txt')
        subs_only_to_input_file = dict(zip(subs_only, input_files))
        subs_only_to_data_table = dict(zip(subs_only, data_table))
        data_table_to_subs_only = dict(zip(data_table, subs_only))

        # Check which output files don't exist, and create a list of them
        subs_only = [file for file in subs_only if file not in os.listdir(output_folder)]
        data_table = [file for file in data_table if file not in os.listdir(output_folder)]
        for file in data_table:
            file = data_table_to_subs_only[file]
            if file not in subs_only:
                subs_only.append(file)

        start_time = time.time()
        for file_no, subs_only_file in enumerate(subs_only):
            # Read in the subtitle file
            input_file = input_folder + '/' + subs_only_to_input_file[subs_only_file]
            full_input = open(input_file, "r", encoding="utf8").read()
            input_lines = full_input.split("\n")

            # Remove any characters not in the whitelist
            output_file = output_folder + '/' + subs_only_file
            output_lines = self._strip_text(input_lines)
            output_lines = pd.DataFrame([output_lines]).transpose()
            output_lines = output_lines[output_lines[0] != '']

            # Parse the subs_only file
            lines_and_line_no = []

            # Need to use a separate list here, and remove entries in case there are duplicate lines
            temp_output_lines = output_lines.copy()
            for index, line in enumerate(temp_output_lines[0]):
                line_no = temp_output_lines.index[temp_output_lines[0] == line].tolist()[0]
                lines_and_line_no.append([line, line_no])
                temp_output_lines.iloc[index, 0] = ''

            word_list = []
            pool = Pool(processes=16)
            for out in pool.starmap(Ichiran.convert_line_to_table_rows, tqdm.tqdm(lines_and_line_no)):
                word_list.extend(out)

            # Write the data to files
            output_lines.to_csv(output_file, sep='\t', header=False)
            data_table = pd.DataFrame(word_list,
                                      columns=['line', 'reading', 'text', 'kana', 'score', 'seq',
                                               'gloss', 'conj_pos', 'conj_type', 'neg', 'dict_reading',
                                               'dict_text', 'dict_kana', 'suffix'])
            data_table.sort_values(by='line', inplace=True)
            data_table.to_csv(output_folder + '/' + subs_only_to_data_table[subs_only_file], index=False, sep='\t')

            passed_time = time.time() - start_time
            est_time = round((passed_time / (file_no+1)) * (len(subs_only) - file_no+1) / 60, 1)
            # TODO after each file, write an event to the queue to update the UI status
            print('Files Complete:', file_no + 1, '/', len(subs_only))
            print('Estimated time remaining:', est_time, 'minutes')
        print('All Files Analysed. Batch Complete!')

    def _strip_text(self, input_lines):
        """Remove all non-Whitelisted characters from the input list of lists"""
        output_lines = []
        for line in input_lines:
            line = re.sub(r'（.+?）', '', line)
            line = re.sub(r'\(.+?\)', '', line)
            line = [character for character in line if self._WHITELIST.search(character)]
            output_lines.append(''.join(line))
        return output_lines

    def _analyse_words(self, data_table):
        # Remove any words that don't have a definition
        data_table = data_table[data_table.gloss != 0]
        number_of_words = len(data_table)

        # Group duplicate rows, counting the number of occurrences, then sort descending by frequency
        unique_words = data_table.groupby(['text']).size().reset_index()
        unique_words.rename(columns={0: 'frequency'}, inplace=True)
        unique_words.sort_values(by=['frequency'], ascending=False, inplace=True)
        unique_words = unique_words.reset_index(drop=True)
        number_of_unique_words = len(unique_words)

        # Read the database and filter known words (status == 1)
        database = db.read_database()
        known_words = database.loc[database['status'] == 1]

        # Compare the known words from the database with the data_table
        unknown_words = self._dataframe_difference(data_table, known_words, 'left_only', True)
        number_of_unknown_words = len(unknown_words)

        unknown_unique_words = self._dataframe_difference(unique_words, known_words, 'left_only', True)
        number_of_unknown_unique_words = len(unknown_unique_words)

        comprehension = round(((number_of_words - number_of_unknown_words) / number_of_words) * 100)

        stats = Stats(
            total_words=number_of_words,
            total_unknown=number_of_unknown_words,
            comprehension=comprehension,
            total_unique=number_of_unique_words,
            unique_unknown=number_of_unknown_unique_words
        )

        return stats

    @staticmethod
    def _dataframe_difference(df_1, df_2, column=None, drop_merge=True):
        """
        Compare two DataFrames and return lines that only appear in df_1 (column='left_only'),
        df_2 (columns='right_only'), or both (columns='both')
        """
        comparison_table = df_1.merge(df_2, indicator=True, how='outer')
        if column in ['left_only', 'right_only', 'both']:
            difference = comparison_table[comparison_table['_merge'] == column]
        else:
            raise Exception('Invalid value for column. Must be one of: \'left_only\', \'right_only\', \'both\'')

        if drop_merge:
            difference = difference.reset_index(drop=True)
            del difference['_merge']

        return difference
