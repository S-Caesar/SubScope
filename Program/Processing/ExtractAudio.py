# -*- coding: utf-8 -*-

from datetime import datetime

import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

import ffmpeg # Note: need to use 'conda install ffmpeg' in Anaconda console the first time uisng this package to get it to work properly
              # Note: also need to run: pip install ffmpeg-python
import cv2 # Note: pip install opencv-python

import imageio
import math

import os

# Take an .mp4 file and extract a screenshot and audio file based on a provided timestamp
# TODO: Would be good if only one video package could be used here
# TODO: Only works with .mp4 files - need to add support for other file types

def createAudio(mainPath, fileType):
    # Create an audio file from a video file
    videoClip = mp.VideoFileClip(r'' + mainPath + fileType) 
    videoClip.audio.write_audiofile(r'' + mainPath + '.mp3')
    return

def createAudioClip(mainPath, lineNo, startStamp, endStamp):
    # from: https://stackoverflow.com/questions/31929538/how-to-subtract-datetimes-timestamps-in-python/31929686
    startTime = datetime.strptime(startStamp, '%H:%M:%S.%f')
    endTime = datetime.strptime(endStamp, '%H:%M:%S.%f')
    duration = endTime - startTime
    
    audioClip = mainPath + '.mp3'
    outputClip = mainPath + '_' + lineNo + '.wav'

    # from: https://stackoverflow.com/questions/65065501/trim-audio-file-using-python-ffmpeg
    audio_input = ffmpeg.input(audioClip, ss=startStamp)
    audio_cut = audio_input.audio.filter('atrim', duration=duration)
    audio_output = ffmpeg.output(audio_cut, outputClip)
    ffmpeg.run(audio_output)
    return

def convertTimestamp(timestamp, conversion):
    # Convert from 00:00:00.000 format
    stampParts = timestamp.split(':')
    
    # Convert to seconds
    if conversion == 's':
        time = float(stampParts[0])*1440 + float(stampParts[1])*60 + float(stampParts[2])
    # Convert to minutes
    elif conversion == 'm':
        time = float(stampParts[0])*60 + float(stampParts[1]) + float(stampParts[2])/60
    # Convert to hours
    elif conversion == 'h':
        time = float(stampParts[0]) + float(stampParts[1])/60 + float(stampParts[2])/1440
    return time

def createScreenshot(mainPath, fileType, lineNo, startStamp, endStamp):
    # Extract a single frame from a video based on a start and end timestamp
    # Convert from 00:00:00.000 format to seconds, then get the midpoint of the start and end time
    startTime = convertTimestamp(startStamp, 's')
    endTime = convertTimestamp(endStamp, 's')   
    midpoint = (endTime - startTime)/2
    
    # Get the FPS of the video
    cap = cv2.VideoCapture(r'' + mainPath + fileType)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate the target frame
    targetFrame = math.floor(midpoint*fps)

    # From: https://stackoverflow.com/questions/64143387/split-video-into-images-with-ffmpeg-python
    # Extract a single frame from the video
    # Use the trimmed video, as it's much faster
    reader = imageio.get_reader(r'' + mainPath + '_' + lineNo + '.mp4')
    
    for frame_number, im in enumerate(reader):
        if frame_number == targetFrame:
            imageio.imwrite(mainPath + '_' + lineNo + '.jpg', im)
            break
    return

def trimVideo(startStamp, endStamp, mainPath, fileType, trimmedVideo):   
    # TODO: can be used to make a shorter clip to extract audio from - currently seems to start too early    
    startTime = convertTimestamp(startStamp, 's')
    endTime = convertTimestamp(endStamp, 's')
    ffmpeg_extract_subclip(r'' + mainPath + fileType, startTime, endTime, targetname=trimmedVideo)
    
    return

def checkForFiles(folder, video, outputType):
    fileList = os.listdir(folder)
    outputName = video + outputType
    
    if outputName in fileList:
        output = True
        print('Output file already exists:', video + outputType)
    else:
        output = False

    return output

'''
'----------------------------------------------------------------------------'
startStamp = '00:00:39.092'
endStamp = '00:00:40.677'

lineNo = '69'

folder = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Subtitles/SteinsGate'
video = 'STEINS;GATE.S01E02.JA'

mainPath = folder + '/' + video

# Will only need to create the audio file for an episode once,
# then it can be split up multiple times for the audio clips/screenshots
if checkForFiles(folder, video, '.mp3') == False:
    createAudio(mainPath)

if checkForFiles(folder, video, '_' + lineNo + '.mp3') == False:
    createAudioClip(mainPath, lineNo, startStamp, endStamp) 

# The trimmed video is used to get the screenshot
if checkForFiles(folder, video, '_' + lineNo + '.mp4') == False:
    trimmedVideo = mainPath + '_' + lineNo + '.mp4'
    trimVideo(startStamp, endStamp, mainPath, trimmedVideo)

if checkForFiles(folder, video, '_' + lineNo + '.jpg') == False:
    createScreenshot(mainPath, lineNo, startStamp, endStamp)
'----------------------------------------------------------------------------'
'''