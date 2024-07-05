import math
import os
import sys
import numpy as np
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip
import wave

from model.media_converter import MediaConverter

class AudioConverter(MediaConverter):
    def __init__(self, file = "", output =  "", output_ext = "wav"):
        MediaConverter.__init__(self, file, output, output_ext)

    def convert(self):
        audio, sr = librosa.load(self.file)
        # Convertendo para mono
        audio_mono = librosa.core.to_mono(audio)
        # Salvando o arquivo de áudio mono
        sf.write(f"{self.output}.{self.output_ext}", audio_mono, sr)
        return f"{self.output}.{self.output_ext}"

    def get_duration(self):
        data, samplerate = sf.read(self.file)
        return len(data) / samplerate

    def get_frame_rate(self):
        with wave.open(self.file, "rb") as wav:
            # Obter informações sobre o arquivo WAV
            params = wav.getparams()
            # A taxa de quadros é o número de quadros por segundo
            frame_rate = params.nframes / params.nchannels / params.sampwidth
            return frame_rate

    @staticmethod
    def create_break(break_name, duration):
        # Definir a taxa de amostragem
        sample_rate = 44100
        # Definir a duração do silêncio em segundos
        # Criar um array NumPy com zeros
        data = np.zeros((math.floor(duration * sample_rate), 2), dtype=np.int16)
        # Salvar o arquivo WAV
        sf.write(break_name, data, sample_rate)
        return break_name

    @staticmethod
    def join_audios(audio1, audio2, output):
        # audio deve ser mono:
        # Carregar os arquivos de áudio
        audio1 = sf.read(audio1)
        audio2 = sf.read(audio2)
        # Concatenar os dados de áudio
        data_final = np.concatenate((audio1[0], audio2[0]))
        # Salvar o arquivo final
        sf.write(output, data_final, audio1[1])
        return output