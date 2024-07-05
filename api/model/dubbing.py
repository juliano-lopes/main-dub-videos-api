from sqlalchemy import Column, String, Integer, DateTime, Float, Text
from model.base import Base

from schemas.dubbing import DubbingViewSchema

#{"video_title": video_title, "dubbed_video": video_data_encoded, "dubbed_audio":file_final_destination, "audio_video_duration":audio_video_duration, "audio_duration":audio_duration, "transcripted_phrases":phrases, "translated_phrases":translation}
class Dubbing(Base):
    __tablename__ = 'dubbing'
    
    id = Column("pk_dubbing", Integer, primary_key=True)
    video_title = Column(String(255), unique=True)
    dubbed_video = Column(Text, unique=True)
    dubbed_audio = Column(String(255), unique=True)
    audio_video_duration = Column(Integer)
    audio_duration = Column(Integer)
    transcription = Column(Text)

    def __init__(self, data: DubbingViewSchema):
        #self.__dict__ = data
        title = data["video_title"].split("-")
        title = " ".join(title)
        self.video_title = title
        self.dubbed_video = data["dubbed_video"]
        self.dubbed_audio = data["dubbed_audio"]
        self.audio_video_duration = data["audio_video_duration"]
        self.audio_duration = data["audio_duration"]
        self.transcription= data["transcription"]
        
    def get_data(self):
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}