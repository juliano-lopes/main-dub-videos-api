import json
import os
import shutil
import sys

import requests
from werkzeug.datastructures import FileStorage
from flask_pydantic_api import UploadedFile, pydantic_api
from pydantic import ValidationError
from model import Session
from model.Video_downloader import VideoDownloader
from model.audio_converter import AudioConverter
from service.authentication import Authentication
from config.config import Config
from model.dubbing import Dubbing
from service.dubbing_service import DubbingService
from schemas.error import ErrorSchema
from schemas.dubbing import DeleteDubbingSchema, DeleteDubbingSuccessSchema, DubbingViewSchema, FileVideoSchema, ListDubbingViewSchema, UpdateDubbingTitleSchema, UrlVideoSchema, show_dubbings, TranscriptionSchema
from util import Util
from model.video_converter import VideoConverter
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request
from urllib.parse import unquote


from sqlalchemy.exc import IntegrityError

from logger import logger
from flask_cors import CORS

info = Info(title="API Dub Videos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app, origins=['*'])

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
dubbing_tag = Tag(name="Dublagem", description="Adição, visualização e remoção de dublagens à base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/dub-transcription', tags=[dubbing_tag],
          responses={"200": TranscriptionSchema, "400": ErrorSchema})
async def get_dub_transcription(form: UrlVideoSchema):
    """ realiza uma dublagem do video passado pela url

    Retorna uma representação dos dados referente à dublagem.
    """
    
    logger.debug(f"dublando video do YouTube com a url: '{form.url}, idioma de origem: {form.original_language}, idioma destino: {form.target_language}'")
    try:
        video_downloader = VideoDownloader(form.url)
        video_title, file_name, file_path = video_downloader.download_youtube_video()
        auth = Authentication(Config.credential_key, Config.bucket_name)
        video = VideoConverter(video_title, file_path, f"{Util.get_paths(file_name)['destination']}", "wav")
        audio_path = video.convert()
        audio = AudioConverter(audio_path, f"{Util.get_paths(file_name)['final_destination']}/audio_original_video_mono_{ Util.get_paths(video_title)['name']}", "wav")
        audio_video_mono = audio.convert()
        audio = AudioConverter(audio_video_mono, Util.get_paths(file_name)['final_destination'], "wav")
        dubbing_service = DubbingService(auth, video, audio, form.original_language, form.target_language)
        data = dubbing_service.make_dubbing()
        print("pegou data, title foi ", data["video_title"])
        return {"uri": "ok"}, 200
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = f"Não foi possível obter uri ({form.url}):\n{e}"
        logger.warning(f"Erro obter uri. {error_msg}")
        return {"message": error_msg}, 400


@app.post('/dubbing-video-url', tags=[dubbing_tag],
          responses={"200": DubbingViewSchema, "400": ErrorSchema})
async def dub_video_by_url(form: UrlVideoSchema):
    """ realiza uma dublagem do video passado pela url

    Retorna uma representação dos dados referente à dublagem.
    """
    
    logger.debug(f"dublando video do YouTube com a url: '{form.url}, idioma de origem: {form.original_language}, idioma destino: {form.target_language}'")
    try:
        video_downloader = VideoDownloader(form.url)
        video_title, file_name, file_path = video_downloader.download_youtube_video()
        auth = Authentication(Config.credential_key, Config.bucket_name)
        video = VideoConverter(video_title, file_path, f"{Util.get_paths(file_name)['destination']}", "wav")
        audio_path = video.convert()
        audio = AudioConverter(audio_path, f"{Util.get_paths(file_name)['final_destination']}/audio_original_video_mono_{ Util.get_paths(video_title)['name']}", "wav")
        audio_video_mono = audio.convert()
        audio = AudioConverter(audio_video_mono, Util.get_paths(file_name)['final_destination'], "wav")
        dubbing_service = DubbingService(auth, video, audio, form.original_language, form.target_language)
        data = dubbing_service.make_dubbing()
        print("pegou data, title foi ", data["video_title"])

        dubbing = Dubbing(data)
        logger.debug("Iniciando a inserção de dubbing feito pela url")
        save_dubbing(dubbing)
        return dubbing.get_data(), 200
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = f"Não foi possível dublar o vídeu ({form.url}):\n{e}"
        logger.warning(f"Erro ao dublar vídeo. {error_msg}")
        return {"message": error_msg}, 400

@app.post('/dubbing-video-file', tags=[dubbing_tag],
          responses={"200": DubbingViewSchema, "400": ErrorSchema})
@pydantic_api()
async def dub_video_by_file(form: FileVideoSchema):
    """ realiza uma dublagem do video  enviado por arquivo

    Retorna uma representação dos dados referente à dublagem.
    """

    try:

        target_language = form.target_language
        original_language = form.original_language
        file = os.path.basename(form.file.filename)
        file = file.split(".")

        if not (len(file) > 1 and isinstance(file[0], str)):
            file = f"video-untitled-{Util.get_paths()['random_name']}.mp4"
        else:
            file = ".".join(file)

        title = Util.get_paths(file)['name']
        file = Util.sanitize_string(file)
        Util.make_dirs(file)
        dir_upload = Util.get_paths(file)['upload']
        file_path = f"{dir_upload}/{file}"
        form.file.save(file_path)
        
        destination = f"{Util.get_paths(file)['destination']}"
        final_destination = f"{Util.get_paths(file)['final_destination']}"

        auth = Authentication(Config.credential_key, Config.bucket_name)
        
        video = VideoConverter(title, file_path, destination, "wav")
        audio_path = video.convert()
        audio = AudioConverter(audio_path, f"{final_destination}/audio_original_video_mono_{Util.get_paths(title)['name']}", "wav")
        audio_video_mono = audio.convert()
        audio = AudioConverter(audio_video_mono, final_destination, "wav")
        dubbing_service = DubbingService(auth, video, audio, original_language, target_language)
        data = dubbing_service.make_dubbing()
        dubbing = Dubbing(data)
        save_dubbing(dubbing)

        #print(f"dados foi {data}")
        return dubbing.get_data(), 200
    except Exception as e:
        print(f"não foi salvo: {e}")
        return {"message":f"erro: {e}"}, 400

def save_dubbing(dubbing: Dubbing):
    try:
        session = Session()
        # salvando dubbing
        session.add(dubbing)
        # efetivando o camando de adição de novo dubbing
        session.commit()
        logger.debug(f"Salvo video de título : '{dubbing.video_title}'")
        print(f"Salvo no banco video de título : '{dubbing.video_title}'")
    except Exception as e:
        logger.debug(f"Erro ao salvar vídeo: '{dubbing.video_title}\n{e}'")
        print(f"Erro ao salvar vídeo no banco: '{dubbing.video_title}\n{e}'")

@app.get('/dubbings', tags=[dubbing_tag], responses= {"200":ListDubbingViewSchema, "400": ErrorSchema, "404": ErrorSchema})
def get_dubbings():
    """ busca vídeos dublados no banco e retorna uma lista de dublagens """
    try:
        data = {"dubbings": []}
        session = Session()
        dubbings = session.query(Dubbing).all()
        if dubbings:
            print(dubbings[0].video_title)
            data = show_dubbings(dubbings)
            return data, 200
        else:
            return {"message": f"Nenhuma dublagem cadastrada"}, 404
    except Exception as e:
        print(f"Não foi possível listar dubbings\n{e}")
        return {"message": f"Não foi possível listar dublagens:\n{e}"}, 400
@app.delete('/dubbings', tags=[dubbing_tag], responses={"200": DeleteDubbingSuccessSchema, "400": ErrorSchema, "404": ErrorSchema})
def delete_dubbing(form: DeleteDubbingSchema):
    """ apaga do banco de dados uma dublagem com base no id passado pelo corpo da requisição """
    id = form.id
    try:
        session = Session()
        count = session.query(Dubbing).filter(Dubbing.id == id).delete()
        session.commit()
        data = {}
        if count:
            data = {"id": id, "message": f"Dublagem apagada com sucesso"}
            return data, 200
        else:
            data = {"message": f"Não existe dublagem com id {id}"}
            return data, 404
    except Exception as e:
        return {"message": f"Ocorreu um erro ao tentar apagar Dublagem com id {id}:\n{e}"}, 400

@app.put('/dubbings', tags=[dubbing_tag], responses={"200": UpdateDubbingTitleSchema, "400": ErrorSchema, "404": ErrorSchema})
async def update_dubbing(form: UpdateDubbingTitleSchema):
    """ atualiza no banco de dados o título de uma dublagem com base no id passado pelo corpo da requisição """
    id = form.id
    title = form.video_title
    try:
        session = Session()
        dubbing = session.query(Dubbing).filter(Dubbing.id == id).first()
        
        #session.commit()
        data = {}
        if dubbing:
            dubbing.video_title = title
            session.commit()
            data = {"id": id, "video_title": title}
            return data, 200
        else:
            data = {"message": f"Não existe dublagem com id {id}"}
            return data, 404
    except Exception as e:
        return {"message": f"Ocorreu um erro ao tentar atualizar Dublagem com id {id}:\n{e}"}, 400
