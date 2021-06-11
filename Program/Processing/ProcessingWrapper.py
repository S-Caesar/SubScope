# -*- coding: utf-8 -*-

# A wrapper for 'FindSentences' and 'ExtractAudio'

import FindSentences as fs
import ExtractAudio as ea

import pandas as pd


'----------------------------------------------------------------------------'
folder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles/SteinsGate'
databaseFile = 'database.txt'

database = pd.read_csv(folder + '/' + databaseFile, sep='\t')

# TODO: issue with getting the right audio clip due to mimatch of subtitles or video (intro watermarks, skipped opening songs, etc.)
targetWord = 'お前'
wordLoc = fs.findSentences(folder, database, targetWord)

textLine = 5
startStamp = wordLoc['timestamp'][textLine][0]
endStamp = wordLoc['timestamp'][textLine][1]

lineNo = str(int(wordLoc['line no'][textLine]))
video = str(wordLoc['episode'][textLine]).replace('_full.txt','')

mainPath = folder + '/' + video

# Will only need to create the audio file for an episode once,
# then it can be split up multiple times for the audio clips/screenshots
if ea.checkForFiles(folder, video, '.mp3') == False:
    ea.createAudio(mainPath)

if ea.checkForFiles(folder, video, '_' + lineNo + '.mp3') == False:
    ea.createAudioClip(mainPath, lineNo, startStamp, endStamp) 

# The trimmed video is used to get the screenshot
if ea.checkForFiles(folder, video, '_' + lineNo + '.mp4') == False:
    trimmedVideo = mainPath + '_' + lineNo + '.mp4'
    ea.trimVideo(startStamp, endStamp, mainPath, trimmedVideo)

if ea.checkForFiles(folder, video, '_' + lineNo + '.jpg') == False:
    ea.createScreenshot(mainPath, lineNo, startStamp, endStamp)