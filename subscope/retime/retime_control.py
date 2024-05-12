import copy
from datetime import datetime

from subscope.options.options import Options
from subscope.retime.retime_events import RetimeEvents
from subscope.retime.retime_state import RetimeState
from subscope.retime.retime_view import RetimeView


class RetimeControl:
    _DIVIDER = ' --> '

    def __init__(self):
        self._state = RetimeState(
            theme=Options.main_theme()
        )
        self._view = RetimeView(
            state=copy.copy(self._state)
        )

    def run(self):
        while True:
            event = self._view.show()
            if event is None:
                break

            elif event.name == RetimeEvents.Navigate.name:
                self._view.close()
                return event.destination

            elif event.name is RetimeEvents.UpdateState.name:
                self._state = event.state

            elif event.name == RetimeEvents.ReopenWindow.name:
                self._view.close()
                self._view = RetimeView(
                    state=self._state
                )

            else:
                self._handle(event)

    def _handle(self, event):
        if event.name == RetimeEvents.RetimeSubs.name:
            self._retime_files(event.selected_files, event.offset)

    def _retime_files(self, selected_files, offset):
        timestamp_errors = []
        for file in selected_files:
            filepath = self._state.folder + '/' + file
            timestamp_error = self._retime_file(filepath, offset)
            if timestamp_error:
                timestamp_errors.append(file)

        if len(timestamp_errors) > 0:
            timestamp_errors = "\n".join(timestamp_errors)
            message = f"Some files were not updated as the offset would make a timestamp negative: {timestamp_errors}."
            self._view.write_event(
                RetimeEvents.UpdateDisplayMessage(
                    message=message
                )
            )
    
    def _retime_file(self, filepath, offset):
        lines = self._read_file_to_list(filepath)
        for line_number, line in enumerate(lines):
            if self._DIVIDER in line:
                line = line.split(self._DIVIDER)
                for idx, timestamp in enumerate(line):
                    seconds = self._convert_timestamp_to_seconds(timestamp)
                    seconds += offset
                    if seconds < 0:
                        return True

                    else:
                        timestamp = self._convert_seconds_to_timestamp(seconds)
                        line[idx] = timestamp

                lines[line_number] = self._DIVIDER.join(line)
        self._write_list_to_file(lines, filepath)

    @staticmethod
    def _read_file_to_list(filepath):
        file = open(filepath, 'r', encoding='utf8').read()
        lines = file.split('\n')
        return lines

    @staticmethod
    def _write_list_to_file(lines, filepath):
        file = '\n'.join(lines)
        open(filepath, 'w', encoding='utf8').write(file)

    @staticmethod
    def _convert_timestamp_to_seconds(timestamp):
        timestamp = timestamp.split(':')
        seconds = float(timestamp[0]) * 3600 \
                  + float(timestamp[1]) * 60 \
                  + float(timestamp[2].replace(',', '.'))
        return seconds

    @staticmethod
    def _convert_seconds_to_timestamp(seconds):
        timestamp = datetime.fromtimestamp(seconds).strftime('%H:%M:%S,%f')[:-3]
        return timestamp
