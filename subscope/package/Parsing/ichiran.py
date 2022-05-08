import json
import subprocess

from subscope.package.Parsing.word import Word
from subscope.package.Options import ManageOptions as mo


class Ichiran:

    @staticmethod
    def convert_line_to_table_rows(line, line_no):
        json_output = Ichiran._parse_line(line)
        entries = []
        for entry in json_output[0][0][0]:
            # If the parsed content has multiple readings, just take the first one
            if 'alternative' in entry[1] or 'components' in entry[1]:
                if 'alternative' in entry[1]:
                    entries.append(entry[1]['alternative'][0])
                    break
                # If there are multiple components, take each of the 'components' as separate entries
                if 'components' in entry[1]:
                    for component in entry[1]['components']:
                        entries.append(component)
                        break
            else:
                # Otherwise, it's a normal entry, so just append it
                entries.append(entry[1])

        # Turn each entry into a list of Word objects; highlight any 'invalid' words for investigation
        word_list = []
        for entry in entries:
            word = Word()
            word.set_properties_with_ichiran_json(entry, line_no)
            word_list.append(word.get_list())
            if word.invalid:
                print('===INVALID===' + str(entry))

        return word_list

    @staticmethod
    def _parse_line(line):
        print(line)
        path = mo.getSetting('paths', 'Ichiran Path')
        console_output = subprocess.check_output('ichiran-cli -f ' + line, shell=True, cwd=path)
        json_output = json.loads(console_output)
        return json_output
