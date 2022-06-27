import os
import pandas as pd
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip

from subscope.package.database.database import Database


class MediaUseCase:

    _START = str(Path(__file__).parent.parent.parent) + '/user/subtitles'
    _VIDEO = 'video'
    _IMAGE = 'image'
    _AUDIO = 'audio'
    _TEXT = 'text'
    _SUBS_ONLY = '_subs_only.txt'
    _SUBS_TYPE = '.srt'

    @classmethod
    def screenshot_and_audio_clip(cls, source, episode, line_number):
        screenshot_path = Database.screenshot(source, episode, line_number)
        audio_clip_path = Database.audio_clip(source, episode, line_number)
        if audio_clip_path is None or screenshot_path is None:
            video_file = cls._get_video_file(source, episode)
            times = cls._read_timestamps(source, episode, line_number)
            video_clip_path = cls._create_video_clip(video_file, source, episode, line_number, times[0], times[1])
            audio_clip_path = cls._create_audio_clip(video_clip_path, source, episode, line_number)
            screenshot_path = cls._create_screenshot(video_clip_path, source, episode, line_number, times[0], times[1])
        return screenshot_path, audio_clip_path

    @classmethod
    def _get_video_file(cls, source, episode):
        video_file_path = None
        file = episode
        for filetype in ['.mp4', '.mkv']:
            if file + filetype in os.listdir(cls._START + '/' + source):
                video_file_path = cls._START + '/' + source + '/' + file + filetype
                break

        if video_file_path is None:
            raise Exception('No valid video files found. Must be .mp4 or .mkv')

        return video_file_path

    @classmethod
    def _read_timestamps(cls, source, episode, line_number):
        subs_only_filepath = cls._START + '/' + source + '/' + episode + cls._SUBS_TYPE
        subs_only_file = pd.read_csv(subs_only_filepath, sep='\t', header=None, skip_blank_lines=False)
        # Work back from the sentence line to find the timestamp
        offset = 0
        while True:
            timestamps = subs_only_file.iloc[line_number - offset, 0]
            if ' --> ' not in timestamps:
                offset += 1
            elif offset > 5:
                raise Exception('Exceeded timestamp check limit. Confirm timestamp separator is " --> ".')
            else:
                timestamps = timestamps.split(' --> ')
                break

        times = []
        for timestamp in timestamps:
            times.append(cls._convert_timestamp(timestamp, 's'))
        # The timestamps tend to end slightly before the end of the audio, so extend the second timestamp slightly
        times[1] = times[1] + 0.1
        return times

    @staticmethod
    def _convert_timestamp(timestamp, conversion):
        """Convert from 00:00:00.000 format to hours [h] / minutes [m] / seconds [s]"""
        timestamp = timestamp.split(':')
        timestamp[2] = timestamp[2].replace(',', '.')
        if conversion == 's':
            time = float(timestamp[0]) * 1440 + float(timestamp[1]) * 60 + float(timestamp[2])
        elif conversion == 'm':
            time = float(timestamp[0]) * 60 + float(timestamp[1]) + float(timestamp[2]) / 60
        elif conversion == 'h':
            time = float(timestamp[0]) + float(timestamp[1]) / 60 + float(timestamp[2]) / 1440
        else:
            raise Exception('Invalid input for "conversion". Must be "s", "m"m or "h"')
        return time

    @classmethod
    def _create_video_clip(cls, video_file_path, source, episode, line_number, start, end):
        if cls._VIDEO not in os.listdir(cls._START + '/' + source):
            os.mkdir(cls._START + '/' + source + '/' + cls._VIDEO)

        output_folder = cls._START + '/' + source + '/' + cls._VIDEO + '/'
        output_file = episode + '_' + str(line_number) + '.mp4'
        video_clip_path = output_folder + output_file
        if output_file not in os.listdir(output_folder):
            with VideoFileClip(video_file_path) as video:
                video.subclip(start, end).write_videofile(video_clip_path, audio_codec='aac')
                video.close()

        return video_clip_path

    @classmethod
    def _create_screenshot(cls, video_clip_path, source, episode, line_number, start, end):
        if cls._IMAGE not in os.listdir(cls._START + '/' + source):
            os.mkdir(cls._START + '/' + source + '/' + cls._IMAGE)

        output_folder = cls._START + '/' + source + '/' + cls._IMAGE + '/'
        output_file = episode + '_' + str(line_number) + '.png'
        screenshot_path = output_folder + output_file
        if output_file not in os.listdir(output_folder):
            midpoint = (end - start) / 2
            with VideoFileClip(video_clip_path) as video:
                video.save_frame(screenshot_path, t=midpoint)
                video.close()
        return output_file

    @classmethod
    def _create_audio_clip(cls, video_clip_path, source, episode, line_number):
        if cls._AUDIO not in os.listdir(cls._START + '/' + source):
            os.mkdir(cls._START + '/' + source + '/' + cls._AUDIO)

        output_folder = cls._START + '/' + source + '/' + cls._AUDIO + '/'
        output_file = episode + '_' + str(line_number) + '.mp3'
        audio_clip_path = output_folder + output_file
        if output_file not in os.listdir(output_folder):
            with VideoFileClip(video_clip_path) as video:
                video.audio.write_audiofile(audio_clip_path)
                video.close()
        return output_file
