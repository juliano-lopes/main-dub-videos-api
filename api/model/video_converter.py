import math
import os
import sys
import numpy as np
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip

from model.media_converter import MediaConverter

class VideoConverter(MediaConverter):
    def __init__(self, title, file, output, output_ext):
        MediaConverter.__init__(self, file, output, output_ext)
        self.title = title

    def convert(self):
        """Converts video to audio using MoviePy library
        that uses `ffmpeg` under the hood"""
        filename, ext = os.path.splitext(self.file)
        clip = VideoFileClip(self.file)
        #if self.output == "":
            #self.output = f"{filename}.{self.output_ext}"
        #else:
            #self.output = f"{self.output}.{self.output_ext}"
        print (f"Writ in {self.output}")
        clip.audio.write_audiofile(f"{self.output}.{self.output_ext}")
        return f"{self.output}.{self.output_ext}"
