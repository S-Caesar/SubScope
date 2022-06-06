import os
import pandas as pd

from subscope.package.general.file_handling import FileHandling as fh


class Database:

    # TODO: get the database path location from the settings file once it is written as a class
    _START = os.getcwd() + '/user/subtitles'
    _DATABASE = 'database.txt'
    _TEXT_FOLDER = 'text'
    _ANALYSED_FILE = '_data_table.txt'

    @classmethod
    def create_database(cls, rebuild=False):
        if cls._DATABASE not in os.listdir(cls._START) or rebuild:
            database = pd.DataFrame(columns=['reading', 'text', 'kana', 'gloss', 'status'])
            database.to_csv(cls._START + '/' + cls._DATABASE, index=False, sep='\t')

        if rebuild:
            cls.populate_database()

    @classmethod
    def read_database(cls):
        database = pd.read_csv(cls._START + '/' + cls._DATABASE, sep='\t')
        return database

    @classmethod
    def write_database(cls, database):
        database.to_csv(cls._START + '/' + cls._DATABASE, index=None, sep='\t')

    @classmethod
    def populate_database(cls, overwrite=False):
        """
        Go through each of the subtitle folders, and update the database with the analysed files
        """
        sources = fh.get_folders(cls._START)
        database = pd.read_csv(cls._START + '/' + cls._DATABASE, sep='\t')
        for source in sources:
            path = cls._START + '/' + source + '/' + cls._TEXT_FOLDER
            analysed_files = fh.get_files(path, extension=cls._ANALYSED_FILE)
            database = cls._update_database(path, analysed_files, database, overwrite)

        database.sort_values(by=['reading'], inplace=True)
        database = database.fillna(0)
        database.iloc[:, 4:] = database.iloc[:, 4:].astype(int)
        database.to_csv(cls._START + '/' + cls._DATABASE, index=False, sep='\t')

    @classmethod
    def _update_database(cls, source_path, analysed_files, database, overwrite):
        """
        Append any new unique dict-form words and details to the database
        For each file, indicate the frequency of the word in its column

        source_path: location for the source '_full.txt' file
        analysed_files: list of '_full.txt' files with all the parsed words and definitions
        database: dataframe of all words, definitions, and frequency in each source
        overwrite: overwrite any existing entries in the database
        """

        # Split the file name up to create the ID for the column
        source_name = source_path.split('/')[-2]
        for file_number, file_name in enumerate(analysed_files):
            entry_name = file_name.replace(cls._ANALYSED_FILE, '')

            entry_number = str(file_number+1)
            while len(entry_number) < 3:
                entry_number = '0' + entry_number

            entry = source_name + '/' + entry_name + '/' + entry_number
            if entry in database and overwrite:
                del database[entry]

            # Check for conjugated words, and replace the main columns with the dict form versions
            # Then just delete the 'dict' columns, as this info is now in the main columns
            if entry not in database:
                data_table = pd.read_csv(source_path + '/' + file_name, sep='\t', index_col=None).fillna(0)
                dict_form_table = data_table.copy()
                cols = {'dict_reading': 'reading',
                        'dict_text': 'text',
                        'dict_kana': 'kana'}

                for idx in dict_form_table.index:
                    for col in cols:
                        if '【' in str(dict_form_table[col][idx]):
                            dict_form_table.loc[dict_form_table.index[idx], cols[col]] = data_table[col][idx]

                for col in cols:
                    del dict_form_table[col]

                # Group duplicates, and store the count of each word in the entry column,
                # then remove liens with no 'gloss' data and append new words
                dict_form_table = dict_form_table.groupby(['reading', 'text', 'kana', 'gloss']).size().reset_index()
                dict_form_table = dict_form_table[dict_form_table.gloss != 0]
                dict_form_table.rename(columns={0: entry}, inplace=True)
                database = database.append(dict_form_table)

                print(file_number+1, '/', str(int(len(analysed_files))), 'files analysed')

        # Aggregate the database (remove duplicates)
        aggregate_dict = {}
        cols = database.columns
        for col in cols:
            if cols.get_loc(col) < 5:
                aggregate_dict[col] = 'first'
            else:
                aggregate_dict[col] = 'sum'

        database = database.groupby(database['reading']).aggregate(aggregate_dict).reset_index(drop=True)
        print('All files analysed')

        return database
