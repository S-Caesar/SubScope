import os
import pandas as pd
import re
import time

from subscope.package.general.file_handling import FileHandling as fh
from subscope.package.Parsing.ichiran import Ichiran
from subscope.package.Parsing import ParsedAnalysis as pa


class AnalysisControl:

    _WHITELIST = re.compile('[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]', re.UNICODE)

    def analyse_subtitles(self, input_folder, files):
        # Create an output folder if it doesn't exist
        output_folder = input_folder + '/text'
        try:
            os.mkdir(output_folder)
        except FileExistsError:
            pass

        # TODO: currently stripping of text is based on .srt files; add support for other types (e.g. .ass)
        self._analyse_files(input_folder, output_folder, files)

        output_table = pd.DataFrame()
        files = fh.renameFiles(files, '_data_table', '.txt')
        for file in files:
            if file in os.listdir(output_folder):
                data_table = pd.read_csv(output_folder + '/' + file, sep='\t')
                output_table = output_table.append(data_table)

        stats = []
        if not output_table.empty:
            output_table.reset_index(drop=True)
            stats = pa.simpleAnalysis(output_table)
        return stats

    def _analyse_files(self, input_folder, output_folder, input_files):
        subs_only = fh.renameFiles(input_files, '_subs_only', '.txt')
        data_table = fh.renameFiles(input_files, '_data_table', '.txt')
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

        for file_no, subs_only_file in enumerate(subs_only):
            # Read in the subtitle file
            input_file = input_folder + '/' + subs_only_to_input_file[subs_only_file]
            input_lines = pd.read_csv(input_file, sep='\n', skip_blank_lines=False, header=None).fillna('')
            input_lines = input_lines[0].to_list()

            # Remove any characters not in the whitelist
            output_file = output_folder + '/' + subs_only_file
            output_lines = self._strip_text(input_lines)
            output_lines = pd.DataFrame([output_lines]).transpose()
            output_lines = output_lines[output_lines[0] != '']

            # Parse the subs_only file
            start_time = time.time()
            word_list = []
            parse_input = output_lines[0].to_list()
            for idx, line in enumerate(parse_input):
                if idx > 0 and idx % 20 == 0:
                    passed_time = time.time() - start_time
                    est_time = round((passed_time / idx) * (len(parse_input) - idx) / 60, 1)
                    print('===================================')
                    print('Rows Complete:', idx, '/', len(parse_input))
                    print('Estimated time remaining:', est_time, 'minutes')
                    print('===================================')

                line_no = output_lines.index[output_lines[0] == line].tolist()[0]
                word_list.extend(Ichiran.convert_line_to_table_rows(line, line_no))

            # Write the data to files
            output_lines.to_csv(output_file, sep='\t', header=False)
            data_table = pd.DataFrame(word_list,
                                      columns=['line', 'reading', 'text', 'kana', 'score', 'seq',
                                               'gloss', 'conj_pos', 'conj_type', 'neg', 'dict_reading',
                                               'dict_text', 'dict_kana', 'suffix'])
            data_table.to_csv(output_folder + '/' + subs_only_to_data_table[subs_only_file], index=False, sep='\t')

            print('Files Complete:', file_no + 1, '/', len(subs_only))
        print('All Files Analysed. Batch Complete!')

    def _strip_text(self, input_lines):
        output_lines = []
        for line in input_lines:
            line = re.sub(r'（.+?）', '', line)
            line = re.sub(r'\(.+?\)', '', line)
            line = [character for character in line if self._WHITELIST.search(character)]
            output_lines.append(''.join(line))
        return output_lines


if __name__ == '__main__':
    os.chdir('C:/Users/Steph/OneDrive/App/SubScope/subscope')
    _main_folder = 'C:/Users/Steph/OneDrive/App/SubScope/subscope/user/subtitles/SteinsGate'
    _main_files = fh.getFiles(_main_folder, '.srt')
    _main_files = _main_files[:2]
    print(_main_files)
    AnalysisControl().analyse_subtitles(_main_folder, _main_files)
