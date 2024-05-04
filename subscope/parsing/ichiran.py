import json
import subprocess

from subscope.parsing.word import Word
from subscope.options.options import Options


class Ichiran:

    @staticmethod
    def convert_line_to_table_rows(line, line_no, debug=False):
        json_output = Ichiran._parse_line(line)
        entries = []
        for entry in json_output[0][0][0]:
            # If the parsed content has multiple readings, just take the first one
            if len(entry) > 1:
                if 'alternative' in entry[1] or 'components' in entry[1]:
                    if 'alternative' in entry[1]:
                        entries.append(entry[1]['alternative'][0])
                    # If there are multiple components, take each of the 'components' as separate entries
                    if 'components' in entry[1]:
                        for component in entry[1]['components']:
                            entries.append(component)
                else:
                    # Otherwise, it's a normal entry, so just append it
                    entries.append(entry[1])

        # Turn each entry into a list of Word objects; highlight any 'invalid' words for investigation
        word_list = []
        for entry in entries:
            word = Word()
            word.set_properties_with_ichiran_json(entry, line_no)
            word_list.append(word.get_list())
            if word.invalid and debug:
                print(line)
                print(str(line_no) + ' ===INVALID=== ' + str(entry))

        return word_list

    @staticmethod
    def _parse_line(line):
        path = Options.ichiran_path()
        console_output = subprocess.check_output('ichiran-cli -f ' + line, shell=True, cwd=path)
        json_output = json.loads(console_output)
        json_output = json.dumps(json_output)
        json_output = json_output.replace('\\"', '^')
        json_output = json_output.replace('\'', '^')
        json_output = json.loads(json_output)
        return json_output
