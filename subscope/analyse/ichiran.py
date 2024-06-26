import json
import subprocess

from subscope.analyse.word import Word
from subscope.settings.settings import Settings


class Ichiran:

    @staticmethod
    def convert_line_to_table_rows(line_no, line, character_names, debug=False):
        name_substitutions = {}
        for name in character_names:
            while name in line:
                index = str(f"_{len(name_substitutions)}_")
                name_substitutions[index] = name
                line = line.replace(name, index)

        json_output = Ichiran.parse_line(line)
        entries = []
        # If placeholder text has been substituted in for Japanese names (which the parse won't detect), then the
        #  top level of the json will be split each time this placeholder text is encountered
        for sentence_part in json_output:
            if isinstance(sentence_part, str):
                if "__" in sentence_part:
                    sentence_part = sentence_part.split("__")
                    for idx, part in enumerate(sentence_part):
                        if not part.startswith("_"):
                            sentence_part[idx] = "_" + part
                        if not part.endswith("_"):
                            sentence_part[idx] = part + "_"
                else:
                    sentence_part = [sentence_part]

                for part in sentence_part:
                    # Part is a placeholder - retrieve the name and add an entry for it
                    name = name_substitutions[part]
                    entries.append(
                        {
                            "reading": name,
                            "text": name,
                            "gloss": "Proper Noun"
                        }
                    )

            else:
                for entry in sentence_part[0][0]:
                    # If the parsed content has multiple readings, just take the first one
                    if len(entry) > 1:
                        if "alternative" in entry[1] or "components" in entry[1]:
                            if "alternative" in entry[1]:
                                entries.append(entry[1]["alternative"][0])
                            # If there are multiple components, take each of the 'components' as separate entries
                            if "components" in entry[1]:
                                for component in entry[1]["components"]:
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
                print(str(line_no) + " ===INVALID=== " + str(entry))

        return word_list

    @staticmethod
    def parse_line(line):
        path = Settings.ichiran_path()
        console_output = subprocess.check_output("ichiran-cli -f " + line, shell=True, cwd=path)
        json_output = json.loads(console_output)
        json_output = json.dumps(json_output)
        json_output = json_output.replace('\\"', "^")
        json_output = json_output.replace('\'', "^")
        json_output = json.loads(json_output)
        return json_output
