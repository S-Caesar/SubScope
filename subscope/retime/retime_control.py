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
            for file in self._state.selected_files:
                self._retime(self._state.folder + '/' + file, self._state.offset)
    
    def _retime(self, path, offset):
        file = open(path, 'r', encoding='utf8').read()
        lines = file.split('\n')
        
        for lineNo, line in enumerate(lines):
            if self._DIVIDER in line:
                line = line.split(self._DIVIDER)
                
                for idx, stamp in enumerate(line):
                    stamp = stamp.split(':')
                    
                    # Convert to seconds and add the offset
                    stamp = float(stamp[0])*3600 \
                          + float(stamp[1])*60 \
                          + float(stamp[2].replace(',', '.'))
                    stamp += offset
                    
                    # TODO: Display error on UI
                    if stamp < 0:
                        print('Timestamp not updated. Offset would make a timestamp negative')
                        return
                        
                    else:
                        # Convert back to timestamp format
                        line[idx] = datetime.fromtimestamp(stamp).strftime('%H:%M:%S,%f')[:-3]
                        
                lines[lineNo] = self._DIVIDER.join(line)
            
        file = '\n'.join(lines)
        open(path, 'w', encoding='utf8').write(file)
