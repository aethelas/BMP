import os
from PIL import Image


class ImageReader:
    def __init__(self):
        self._last_error = ""

    @property
    def last_error(self):
        return self._last_error

    def load(self, path):
        self._last_error = ""
        if not path or not os.path.isfile(path):
            self._last_error = "Файл не найден"
            return None
        try:
            with Image.open(path) as image:
                image.load()
                return image.copy()
        except Exception as error:
            self._last_error = str(error)
            return None
