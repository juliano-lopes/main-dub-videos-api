from pytube import YouTube
from util import Util

class VideoDownloader:
    def __init__(self, url):
        self.url = url
    
    def download_youtube_video(self):
        # passing the url to the YouTube object
        my_video = YouTube(self.url)
        video_title = my_video.title
        file_name = Util.get_paths(video_title)['name']
        file_name = f"{file_name}.mp4"
        Util.make_dirs(file_name)
        final_destination = Util.get_paths(file_name)['final_destination']
        file_final_destination = f"{Util.get_paths(file_name)['final_destination']}/{file_name}"

        # downloading the video in high resolution
        my_video.streams.get_highest_resolution().download(final_destination, file_name)
        # return the video title, name and path
        return video_title, file_name,  file_final_destination
