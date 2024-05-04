# -*- coding: utf-8 -*-

from datetime import datetime

class RetimeControl:
    
    _DIVIDER = ' --> '
    
    def retime(self, path, offset):
        
        file = open(path, 'r', encoding='utf8').read()
        lines = file.split('\n')
        
        for lineNo, line in enumerate(lines):
            if self._DIVIDER in line:
                line = line.split(self._DIVIDER)
                
                for idx, stamp in enumerate(line):
                    stamp = stamp.split(':')
                    
                    #Convert to seconds and add the offset
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