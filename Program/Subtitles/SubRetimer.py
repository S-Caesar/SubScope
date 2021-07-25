# -*- coding: utf-8 -*-

# Change the subtitle timestamps by a given offset (in seconds)

import math

def retime(folder, subFile, offset):
    inFile = open(folder + '/' + subFile, 'r', encoding="utf8").read()
    file = inFile.split('\n')
    
    for x in range(len(file)):
        if ' --> ' in file[x]:
            file[x] = file[x].split(' --> ')
            
            for y in range(len(file[x])):
                file[x][y] = file[x][y].split(':')
            
                # Convert to seconds and add offset
                time = float(file[x][y][0])*3600 + \
                       float(file[x][y][1])*60 + \
                       float(file[x][y][2].replace(',','.'))
                       
                time = time + offset    
                
                hours = math.floor(time/3600)
                mins = math.floor((time-(hours*3600))/60)
                secs = str(round((time-(hours*3600)-(mins*60)), 3)).split('.')
                
                if len(str(hours)) == 1:
                    hours = '0' + str(hours)

                if len(str(mins)) == 1:
                    mins = '0' + str(mins)                
                
                if len(str(secs[0])) == 1:
                    secs[0] = '0' + str(secs[0])
                    
                if len(str(secs[1])) == 1:
                    secs[1] = str(secs[1]) + '00'

                elif len(str(secs[1])) == 2:
                    secs[1] = str(secs[1]) + '0'
                    
                secs = ','.join(secs)
                    
                file[x][y] = ':'.join([str(hours), str(mins), str(secs)])
                
            file[x] = ' --> '.join(file[x])

    file = '\n'.join(file)
    
    open(folder + '/' + subFile, 'w', encoding="utf8").write(file)
    
    return