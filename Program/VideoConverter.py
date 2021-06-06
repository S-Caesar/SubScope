# -*- coding: utf-8 -*-

# Convert .mkv to .mp4

import os
import moviepy.editor as mp

from tkinter import Tk
from tkinter.filedialog import askdirectory

root = Tk()

folder = askdirectory(title='Select Folder')

root.withdraw()


files = os.listdir(folder)

videos = [x for x in files if x.endswith('.mkv')]

# Reformat video files to .mp3
for x in range(len(videos)):
    # from: https://zulko.github.io/moviepy/getting_started/videoclips.html
    inputFile = mp.VideoFileClip(folder + '/' + videos[x])
    
    # from: https://zulko.github.io/moviepy/ref/videofx/moviepy.video.fx.all.resize.html
    resizeFile = inputFile.resize(height=360)
    
    videos[x] = videos[x].split('.')
    del videos[x][-1]
    ''.join(videos[x])
    
    videos[x] = videos[x][0]
    
    resizeFile.write_videofile(folder + '/' + videos[x] + '.mp4')