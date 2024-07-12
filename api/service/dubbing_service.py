import base64
import io
import json
import math
import os
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from google.cloud import speech 
from google.cloud import texttospeech
import requests

from model.audio_converter import AudioConverter

from service.authentication import Authentication
from model.video_converter import VideoConverter
from util import Util

class DubbingService:
    def __init__(self, auth: Authentication, video_converter: VideoConverter, audio_converter: AudioConverter, transcript_language: str, translate_language: str):
        self.auth = auth
        self.video_converter = video_converter
        self.audio_converter = audio_converter
        self.transcript_language = transcript_language
        self.translate_language = translate_language
        
    def upload_blob(self):
        path, file_name = self.audio_converter.get_path_file_name()
        blob = self.auth.get_bucket().blob(file_name)
        blob.upload_from_filename(f"{path}/{file_name}")
        gcs_uri = f"gs://{self.auth.get_bucket_name()}/{file_name}"
        return gcs_uri

    def delete_blob(self, nome_blob):
        blob = self.auth.get_bucket().blob(nome_blob)
        blob.delete()
    def make_dubbing(self):
        transcription_api = f"http://{os.environ["T_HOST"]}:5001/transcription_gen_ai"
        speech_api = f"http://{os.environ["S_HOST"]}:5002/speech"
        print(f"Endereços APIs: {transcription_api}. {speech_api}.")

        destination = Util.get_paths(self.video_converter.file)['destination']
        final_destination = Util.get_paths(self.video_converter.file)['final_destination']
        print(f"destination: {destination}\nfinal_destination: {final_destination}")
        #uri="gs://b_dub_videos/audio_original_video_mono_MVPDubVideos-Desenvolvimentofu.wav"
        uri = self.upload_blob()
        
        data_json = {
            "audio_language":self.transcript_language,
            "translation_language":self.translate_language,
            "uri":uri
        }
        print("enviando data para transcricao, ", data_json)
        r_transcription = requests.post(transcription_api, data_json)
        print("resultado")
        print(r_transcription.status_code)
        print(r_transcription.json())
        if r_transcription.status_code==200:
            print("chamando api de conversao de texto para audio")
            transcription = json.dumps(r_transcription.json())
            speech_data = {
                "original_language":self.transcript_language,
                "target_language":self.translate_language,
                "transcription":transcription
            }
            r_speech = requests.post(speech_api, speech_data)
            if r_speech.status_code==200:
                print("api speech retornou 200")
                #print(r_speech.json())
            else:
                print("api speech nao retornou 200, ", r_speech.status_code)
                raise Exception(r_speech.json())
        else:
            raise Exception(r_transcription.json())

        file_final_destination = f"{final_destination}/dubbing_audio_final_{Util.get_paths(self.video_converter.title)['name']}.wav"
        blob_name = r_speech.json()
        blob_name = blob_name["blob_name"]
        print("blob name foi ", blob_name)
        blob = self.auth.get_bucket().blob(blob_name)
        with open(file_final_destination, "wb") as f:
            blob.download_to_file(f)

        # juntar audio e video:
        print("blob baixado para o caminho ", file_final_destination)
        # Carregar o vídeo e o áudio
        audio_duration = AudioConverter(file_final_destination,final_destination, "wav")
        audio_duration = audio_duration.get_duration()
        audio_video_duration = AudioConverter(self.audio_converter.file, final_destination, "wav")
        audio_video_duration = audio_video_duration.get_duration()
        factor = audio_video_duration / audio_duration
        #audio, sr = librosa.load(file_final_destination)
        #audio = librosa.effects.time_stretch(audio, rate=factor)
        #file_final_destination_speedup = f"{final_destination}/dubbing_service_speedup.wav"
        #sf.write(file_final_destination_speedup, audio, sr)
        video = VideoFileClip(self.video_converter.file)
        #audio = AudioFileClip(file_final_destination_speedup)
        audio = AudioFileClip(file_final_destination)
        # Ajustar o volume do vídeo e do áudio
        volume_video = 0.1
        volume_audio = 1.0

        # Criar o áudio combinado
        combined_audio = CompositeAudioClip([video.audio.volumex(volume_video), audio.volumex(volume_audio)])

        # Combinar o vídeo com o áudio combinado
        combined = video.set_audio(combined_audio)

        # Gerar o novo arquivo MP4
        dubbed_video = f"{final_destination}/dubbed_video_{Util.get_paths(self.video_converter.title)['name']}.mp4"
        combined.write_videofile(dubbed_video)
        with open(dubbed_video, "rb") as video_file:
            video_buffer = io.BytesIO(video_file.read())
        video_data_encoded = base64.b64encode(video_buffer.getvalue()).decode('utf-8')
        print(f"Duração audio original do video: {audio_video_duration}")
        print(f"Duração audio ssml gerado: {audio_duration}")
        print(f"idioma origem: {self.transcript_language}, idioma destino: {self.translate_language}")
        return {"video_title": self.video_converter.title, "dubbed_video": video_data_encoded, "dubbed_audio":file_final_destination, "audio_video_duration":audio_video_duration, "audio_duration":audio_duration, "transcription":transcription}