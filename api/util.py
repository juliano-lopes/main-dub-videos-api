import datetime
import os
from unidecode import unidecode

class Util:
    @staticmethod
    def make_dirs(file):
        if not os.path.exists(Util.get_paths(file)['destination']):
            os.makedirs(Util.get_paths(file)['destination'])
        if not os.path.exists(Util.get_paths(file)['final_destination']):
            os.makedirs(Util.get_paths(file)['final_destination'])
        if not os.path.exists(Util.get_paths(file)['upload']):
            os.makedirs(Util.get_paths(file)['upload'])

    @staticmethod
    def get_paths(file = ""):
        max_length = 30
        base_path = "dubbings/temp"
        random_name = Util.getCurrentDatetime()
        name = os.path.basename(file)
        name = Util.sanitize_string(name)
        if "." in name:
            name = name.split(".")
            if len(name) > 1:
                name.pop()
                name = "-".join(name)
        if len(name) > max_length:
            name = name[:max_length]
        destination = f"{base_path}/{name}"
        final_destination = f"dubbings/{name}"
        upload = f"dubbings/{name}/upload"
        return {"base_path":base_path, "name":name, "destination":destination, "final_destination":final_destination, "upload": upload, "random_name":random_name}

    @staticmethod
    def timestamp_to_seconds(timestamp):
        format = ""
        if "." in timestamp:
            format = "%H:%M:%S.%f"
        elif "," in timestamp:
            format = "%H:%M:%S,%f"
        else:
            format = "%H:%M:%S"

        datetime_object = datetime.datetime.strptime(timestamp, format)
        return round(datetime_object.second + datetime_object.minute * 60 + datetime_object.hour * 3600 + datetime_object.microsecond / 1000000)

    @staticmethod
    def getCurrentDatetime():
        time = datetime.datetime.now()
        return f"{time.day}{time.month}{time.year}-{time.hour}{time.minute}{time.second}"

    def sanitize_string(name):
        name = unidecode(name)
        invalid_characters = "\\/:*?\"<>| "
        translate_table = str.maketrans("", "", invalid_characters)
        return name.translate(translate_table)
