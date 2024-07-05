import abc

class MediaConverter(abc.ABC):
    def __init__(self, file, output, output_ext):
        self.file = file
        self.output_ext = output_ext
        self.output = output

    @abc.abstractmethod
    def convert(self):
        raise NotImplementedError()
    
    def get_path_file_name(self):
        path = "."
        file_name = self.file
        splitter = "/"
        if splitter in file_name:
            path = file_name.split(splitter)
            file_name = path.pop()
            path = "/".join(path)
        return path, file_name