import os
import pandas as pd
import re
import subprocess
import json
import time

from subscope.package.general.file_handling import FileHandling as fh
from subscope.package.Options import ManageOptions as mo
from subscope.package.Parsing import ParsedAnalysis as pa


class AnalysisControl:

    # From: https://stackoverflow.com/questions/2718196/find-all-chinese-text-in-a-string-using-python-and-regex
    _WHITELIST = re.compile('[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]', re.UNICODE)

    def analyse_subtitles(self, input_folder, files):
        # Create an output folder if it doesn't exist
        output_folder = input_folder + '/text'
        try:
            os.mkdir(output_folder)
        except FileExistsError:
            pass

        # TODO: currently stripping of text is based on .srt files;
        #       need to add support for other types (e.g. .ass)
        # TODO: use multiprocessing to split files up and analyse them faster
        self._create_subs_only_files(input_folder, output_folder, files)

        # TODO: combine the subs_only and data_table processes so they are done together,
        #       rather than doing all of the subs_only then all of the data_table

        output_table = pd.DataFrame()
        for file in files:
            try:
                file = fh.renameFiles(file, '_data_table', '.txt')
                data_table = pd.read_csv(output_folder + '/' + file[0], sep='\t')
                output_table = output_table.append(data_table)
            except FileNotFoundError:
                # TODO: remove this once the function is properly set up to analyse all files
                print('File not found')
                continue
        output_table.reset_index(drop=True)
        stats = pa.simpleAnalysis(output_table)
        return stats

    def _create_subs_only_files(self, input_folder, output_folder, files):
        subs_only = fh.renameFiles(files, '_subs_only', '.txt')
        data_table = fh.renameFiles(files, '_data_table', '.txt')
        files_dict = dict(zip(subs_only, files))
        analysis_dict = dict(zip(subs_only, data_table))
        data_table = pd.DataFrame(columns=['line', 'reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])
        for file_no, file_name in enumerate(subs_only):
            # TODO: change this so all the files will be checked, and created if they don't exist, for
            #       both subs_only and data_table
            if file_name not in os.listdir(output_folder):
                # Read in the subtitle file
                input_file = input_folder + '/' + files_dict[file_name]
                input_lines = pd.read_csv(input_file, sep='\n', skip_blank_lines=False, header=None).fillna('')
                input_lines = input_lines[0].to_list()

                # Remove any characters not in the whitelist
                output_file = output_folder + '/' + file_name
                output_lines = self._strip_text(input_lines)
                output_lines = pd.DataFrame([output_lines]).transpose()
                output_lines = output_lines[output_lines[0] != '']

                # Parse the subs_only file
                parse_input = output_lines[0].to_list()

                start_time = time.time()
                for idx, line in enumerate(parse_input):
                    if idx > 0 and idx % 20 == 0:
                        passed_time = time.time() - start_time
                        est_time = round((passed_time / idx) * (len(parse_input) - idx) / 60, 1)
                        print('===================================')
                        print('Rows Complete:', idx, '/', len(parse_input))
                        print('Estimated time remaining:', est_time, 'minutes')
                        print('===================================')

                    line_no = output_lines.index[output_lines[0] == line].tolist()[0]
                    json_output = self.ichiran_parse(line)
                    flat_json = self.flatten_ichiran(json_output)
                    data_table = data_table.append(flat_json)
                    data_table['line'] = data_table['line'].fillna(line_no).astype(int)

                # Remove 'conj' / 'compound' / 'components' columns if existing
                del_columns = ['conj', 'compound', 'components']
                for item in del_columns:
                    if item in data_table:
                        del data_table[item]

                # Write the data to files
                output_lines.to_csv(output_file, sep='\t', header=False)
                data_table.to_csv(output_folder + '/' + analysis_dict[file_name], index=False, sep='\t')

                # TODO: correct this so it doesn't include skipped files
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

    @staticmethod
    def ichiran_parse(line):
        print(line)
        path = mo.getSetting('paths', 'Ichiran Path')
        console_output = subprocess.check_output('ichiran-cli -f ' + line, shell=True, cwd=path)
        json_output = json.loads(console_output)
        return json_output

    @staticmethod
    def flatten_ichiran(json_output):
        # Main list where each element is [word, information]
        main_json = json_output[0][0][0]
        main_table = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss', 'conj'])

        for idx, entry in enumerate(main_json):
            # If the parsed content has multiple readings, just take the first one
            if 'alternative' in main_json[idx][1]:
                main_json[idx][1] = main_json[idx][1]['alternative'][0]
            # If there are multiple components, take 'components' for normalising
            if 'components' in main_json[idx][1]:
                main_json[idx][1] = main_json[idx][1]['components']
            main_table = main_table.append(pd.json_normalize(main_json[idx][1])).reset_index(drop=True)

        output_table = pd.DataFrame(columns=['reading', 'text', 'kana', 'score', 'seq', 'gloss',
                                             'conj-prop', 'conj-type', 'neg', 'dict-reading',
                                             'dict-text', 'dict-kana'])
        for idx in range(len(main_table)):
            # If 'conj' is an empty list, then it's a normal word, so just append it
            if main_table['conj'][idx] == list():
                output_table = output_table.append(main_table[idx:idx+1])
            # If there is Nan in the 'conj' column then skip it (probably a name)
            elif main_table[idx:idx+1]['conj'].isnull().values.any():
                continue
            # Else, there is data for the 'conj' column; extract and reformat
            else:
                base_data = main_table[idx:idx+1].copy()
                # Flatten to: 'prop', 'via', 'readok'
                # Or: 'prop', 'reading', 'gloss', 'readok'
                conj_data = pd.json_normalize(main_table['conj'][idx])

                # Flatten to: 'pos', 'type', 'neg' (if conj is negative)
                pos_data = pd.json_normalize(conj_data['prop'][0])

                # If conj. is 'via' a previous conj. (e.g. Past form of Potential form),
                # then 'via' must be flattened to get the same data as in posData
                if len(conj_data.columns) == 3:
                    # Flatten to: 'prop', 'reading', 'gloss', 'readok'
                    conj_data = pd.json_normalize(conj_data['via'][0])

                    # Flatten to: 'pos', 'type', 'neg' (if conj is negative)
                    via_pos_data = pd.json_normalize(conj_data['prop'][0])

                    # Append the posData conjugation to each element of viaPosData
                    pos_data['pos'][0] = pos_data['pos'][0] + ' [via] ' + via_pos_data['pos'][0]
                    pos_data['type'][0] = pos_data['type'][0] + ' [via] ' + via_pos_data['type'][0]

                # Rename the columns to match main DataFrame
                pos_data = pos_data.rename(columns={'pos': 'conj-prop', 'type': 'conj-type'})

                # Get the dictionary form of the word, and create columns to store
                # the same data as for the main word ('reading', 'text', 'kana')
                # Split the 'reading' info for the dict form to get the kanji and kana
                dict_split = conj_data['reading'][0].split(' ')

                # If the word doesn't have kanji, then there will be no kanji
                # /reading to split, and the result is a single element which
                # will need to fill all three spaces
                if len(dict_split) == 1:
                    dict_text = dict_split[0]
                    dict_kana = dict_split[0]

                # If the word does have kanji, it will be split into the kanji,
                # and a reading surrounded by brackets
                else:
                    dict_text = dict_split[0]
                    dict_kana = dict_split[1].replace('【', '').replace('】', '')

                # Put all the dictionary data into a table
                dict_data = pd.DataFrame(
                    {'dict-reading': conj_data['reading'], 'dict-text': dict_text, 'dict-kana': dict_kana})

                # Nest level for 'gloss' depends on whether there was a 'via'
                if len(base_data['conj'][idx][0]) == 4:
                    base_data['gloss'][idx] = base_data['conj'][idx][0]['gloss']
                else:
                    base_data['gloss'][idx] = base_data['conj'][idx][0]['via'][0]['gloss']

                # 'conj' column should now be empty, so just get rid of it
                base_data = base_data.drop(columns=['conj'])
                base_data = base_data.reset_index(drop=True)

                output_data = base_data.join(pos_data).join(dict_data)
                output_table = output_table.append(output_data)

        # Reset the index, as otherwise every entry will be row index 0
        # Then replace all the 'nan' with '0' to avoid any issues later
        output_table = output_table.reset_index(drop=True)
        output_table = output_table.fillna(0)
        return output_table


if __name__ == '__main__':
    os.chdir('C:/Users/Steph/OneDrive/App/SubScope/subscope')
    _main_folder = 'C:/Users/Steph/OneDrive/App/SubScope/subscope/user/subtitles/SteinsGate'
    _main_files = fh.getFiles(_main_folder, '.srt')
    AnalysisControl().analyse_subtitles(_main_folder, _main_files)
