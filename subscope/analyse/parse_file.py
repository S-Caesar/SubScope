import os
import re
from multiprocessing import Pool
import tqdm

import pandas as pd

from subscope.analyse.ichiran import Ichiran
from subscope.shared.file_ext import FileExt
from subscope.shared.sep import Sep
from subscope.utilities.file_handling import FileHandling as fh


class ParseFile:
    _WHITELIST = re.compile("[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]", re.UNICODE)
    _SUBS_ONLY_SUFFIX = "_subs_only"
    _DATA_TABLE_SUFFIX = "_data_table"

    def __init__(self, input_filename, input_folder, output_folder, character_names):
        self._input_filename = input_filename
        self._input_folder = input_folder
        self._output_folder = output_folder
        self._subs_only_filename = fh.rename_file(input_filename, self._SUBS_ONLY_SUFFIX, FileExt.TXT)
        self._data_table_filename = fh.rename_file(input_filename, self._DATA_TABLE_SUFFIX, FileExt.TXT)
        self._character_names = character_names

        self._create_subs_only_file()
        self._create_data_table_file()

    def _create_subs_only_file(self):
        if self._subs_only_filename not in os.listdir(self._output_folder):
            input_filepath = os.path.join(self._input_folder, self._input_filename)
            subs_only_filepath = os.path.join(self._output_folder, self._subs_only_filename)
            if self._input_filename.endswith(FileExt.SRT):
                self._create_subs_only_file_srt(input_filepath, subs_only_filepath)
            else:
                raise Exception(f"Input file type not valid for analysis: {self._input_filename}")

    def _create_subs_only_file_srt(self, input_filepath, subs_only_filepath):
        input_lines = open(input_filepath, "r", encoding="utf8").read().split(Sep.NEW_LINE)
        stripped_lines = self._strip_text(input_lines)
        with open(subs_only_filepath, "w") as f:
            for line_no, line in enumerate(stripped_lines):
                if line != "":
                    if line_no == len(stripped_lines)-1:
                        f.write(f"{line_no}\t{line}")
                    else:
                        f.write(f"{line_no}\t{line}\n")

    def _strip_text(self, input_lines):
        """Remove all non-Whitelisted characters from the input list of lists"""
        output_lines = []
        for line in input_lines:
            line = re.sub(r"（.+?）", "", line)
            line = re.sub(r"\(.+?\)", "", line)
            line = [character for character in line if self._WHITELIST.search(character)]
            output_lines.append(''.join(line))
        return output_lines

    def _create_data_table_file(self):
        if self._data_table_filename not in os.listdir(self._output_folder):
            subs_only_filepath = os.path.join(self._output_folder, self._subs_only_filename)
            subs_only_lines = open(subs_only_filepath, "r", encoding="utf8").read().split(Sep.NEW_LINE)
            # Remove any blank lines at the end of the file as these will cause an error
            while subs_only_lines[-1] == "":
                subs_only_lines = subs_only_lines[:-1]

            indexed_lines = []
            for line in subs_only_lines:
                line_no, line = line.split(Sep.TAB)
                indexed_lines.append([int(line_no), line, self._character_names])

            word_list = self._parse_lines(indexed_lines)
            data_table = pd.DataFrame(
                word_list,
                columns=[
                    "line", "reading", "text", "kana", "score", "seq", "gloss", "conj_pos", "conj_type", "neg",
                    "dict_reading", "dict_text", "dict_kana", "suffix"
                ]
            )
            data_table.sort_values(by="line", inplace=True)
            data_table_filepath = os.path.join(self._output_folder, self._data_table_filename)
            data_table.to_csv(data_table_filepath, index=False, sep=Sep.TAB)

    @staticmethod
    def _parse_lines(indexed_lines):
        word_list = []
        pool = Pool(processes=16)
        for out in pool.starmap(Ichiran.convert_line_to_table_rows, tqdm.tqdm(indexed_lines)):
            word_list.extend(out)
        return word_list
