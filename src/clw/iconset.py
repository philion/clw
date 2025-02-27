"""manage weather icons as a set"""
import logging
from pathlib import Path
from abc import ABC, abstractmethod
import json
from importlib.resources import read_text, read_binary

from PIL import Image
import requests

from . import TIMEOUT

log = logging.getLogger(__name__)


# cheap in-memory cache
_item_cache = {}
def _get(key:str):
    return _item_cache.get(key, None)
def _put(key:str, value):
    existing = _item_cache.get(key, None)
    _item_cache[key] = value
    return existing


class IconSet(ABC):
    """a set of icons for display"""
    def __init__(self):
        super().__init__()
        self._codes = self.load_weather_codes()


    @abstractmethod
    def load_image(self, filename:str):
        """load an image"""


    @abstractmethod
    def load_weather_codes(self) -> dict:
        """load the codes"""


    def lookup_code(self, wmo_code: str):
        """return a day, night, image-url and description for given code"""
        return self._codes.get(wmo_code)


    def _get(self, wmo_code: str, tod: str) -> dict:
        """get a png filename for a code and hour of day"""
        # allow "3", "3wmo" and "3wmo code"
        if wmo_code.endswith("wmo code"):
            wmo_code = wmo_code[:-8]

        if wmo_code.endswith("wmo"):
            wmo_code = wmo_code[:-3]

        return self.lookup_code(wmo_code)[tod]


    def get_image(self, wmo_code: str, tod: str) -> Image:
        """load an image for the code"""
        filename =  self._get(wmo_code, tod)['image']
        return self.load_image(filename)


    def get_description(self, wmo_code: str, tod: str) -> str:
        """get the description for the code"""
        return self._get(wmo_code, tod)['description']


class CachedIconSet(IconSet):
    """cache the images in the image set"""
    def __init__(self, wrapped: IconSet):
        self._wrapped = wrapped
        super().__init__()


    def load_weather_codes(self) -> dict:
        return self._wrapped.load_weather_codes()


    def load_image(self, filename:str) -> Image:
        image = _get(filename)
        if not image:
            image = self._wrapped.load_image(filename)
            _put(filename, image)
        return image


class LocalIconSet(IconSet):
    """load icons from the local file system"""

    def __init__(self, name:str):
        self.name = name
        super().__init__()


    def load_weather_codes(self) -> dict:
        """load the weather codes"""
        #path = Path(self.name, "weather-codes.json")
        #name = "data/png"
        path = Path(self.name, "weather-codes.json")
        result = json.loads(read_text(__package__, path))
        return result

        #log.error(f">>>> {clw} {path}")


    def load_image(self, filename:str) -> Image:
        """load the give image"""
        name = Path(self.name, filename)
        log.debug("loading image: %s", name)
        return Image.open(name)


class HttpIconSet(IconSet):
    # FIXME add init with session, use for requests
    """load icons from the web"""
    def load_weather_codes(self) -> dict:
        """load the codes"""
        with open("weather-codes.json", encoding="utf-8") as f:
            return json.load(f)

    def load_image(self, filename:str) -> Image:
        """load the image"""
        log.debug("loading image url: %s", filename)
        return Image.open(requests.get(filename, stream=True, timeout=TIMEOUT).raw)
