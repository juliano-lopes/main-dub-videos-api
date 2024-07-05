from io import BytesIO
from typing import List
from pydantic import BaseModel, FilePath, Field
from flask_pydantic_api import UploadedFile, pydantic_api
import werkzeug


class FileVideoSchema(BaseModel):
    """ Define como um video para dublagem será representado para inserção
    """
    file: UploadedFile
    original_language: str = "pt-BR"
    target_language: str = "en-US"

class UrlVideoSchema(BaseModel):
    """ Define como um video para dublagem será representado para inserção
    """
    url: str = Field("https://youtu.be/tfAVGTcRtCA", description="URL de um vídeo no YouTube")
    original_language: str = "pt-BR"
    target_language: str = "en-US"

class DubbingViewSchema(BaseModel):
    """
    define como uma dublagem será retornada
    """
    video_title: str = "Título do vídeo"
    dubbed_video: str = "base64" 
    dubbed_audio: str = "dubbing/temp/video_name/video.mp4"
    audio_video_duration: int = 50
    audio_duration: int = 50 
    transcription: str = '{"transcripted_phrases":[{}]}'

class ListDubbingViewSchema(BaseModel):
    dubbings: List[DubbingViewSchema]
def show_dubbings(dubbings: List[DubbingViewSchema]):
    """ return a list of dubbings according to the DubbingViewSchema """
    data = []
    for dubbing in dubbings:
        data.append(dubbing.get_data())
    return {"dubbings": data}

class DeleteDubbingSchema(BaseModel):
    id: int = 1

class DeleteDubbingSuccessSchema(BaseModel):
    id: int = 1
    message: str = "Dublagem apagada com sucesso"

class TranscriptionSchema(BaseModel):
    uri: str = "gs://resource.wav"