import os

import pandas as pd

from subscope.shared.file_ext import FileExt
from subscope.shared.sep import Sep
from subscope.utilities.file_handling import FileHandling as fh
from subscope.database.database import Database as db


class Stats:
    _DATA_TABLE_SUFFIX = "_data_table"

    def __init__(
            self, total_words=None, total_unknown=None, comprehension=None, total_unique=None, unique_unknown=None
    ):
        self.total_words = total_words or "-"
        self.total_unknown = total_unknown or "-"
        self.comprehension = comprehension or "-"
        self.total_unique = total_unique or "-"
        self.unique_unknown = unique_unknown or "-"

    def analyse(self, output_folder, input_filenames):
        output_data_table = self._read_data_table_files_to_dataframe(output_folder, input_filenames)
        self._analyse_data_table(output_data_table)

    def _read_data_table_files_to_dataframe(self, output_folder, input_files):
        data_table_files = fh().rename_files(input_files, self._DATA_TABLE_SUFFIX, FileExt.TXT)
        output_tables = []
        for data_table_file in data_table_files:
            if data_table_file in os.listdir(output_folder):
                filepath = os.path.join(output_folder, data_table_file)
                data_table = pd.read_csv(filepath, sep=Sep.TAB).fillna(0)
                output_tables.append(data_table)
        output_table = pd.concat(output_tables)
        return output_table

    def _analyse_data_table(self, output_table):
        if not output_table.empty:
            output_table.reset_index(drop=True)
            self._analyse_words(output_table)
            db.populate_database()

    def _analyse_words(self, data_table):
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

        self.total_words = number_of_words
        self.total_unknown = number_of_unknown_words
        self.comprehension = comprehension
        self.total_unique = number_of_unique_words
        self.unique_unknown = number_of_unknown_unique_words

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
