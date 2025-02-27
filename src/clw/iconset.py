"""manage weather icons as a set"""
import logging
from pathlib import Path
from abc import ABC, abstractmethod
import json
from importlib.resources import read_text, read_binary
from io import BytesIO

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


HACK_CODE_JSON = """
{
  "0": {
    "day": {
      "description": "Sunny",
      "image": "clear-day.png"
    },
    "night": {
      "description": "Clear",
      "image": "clear-night.png"
    }
  },
  "1": {
    "day": {
      "description": "Mainly Sunny",
      "image": "clear-day.png"
    },
    "night": {
      "description": "Mainly Clear",
      "image": "clear-night.png"
    }
  },
  "2": {
    "day": {
      "description": "Partly Cloudy",
      "image": "partly-cloudy-day.png"
    },
    "night": {
      "description": "Partly Cloudy",
      "image": "partly-cloudy-night.png"
    }
  },
  "3": {
    "day": {
      "description": "Cloudy",
      "image": "cloudy.png"
    },
    "night": {
      "description": "Cloudy",
      "image": "cloudy.png"
    }
  },
  "45": {
    "day": {
      "description": "Foggy",
      "image": "fog-day.png"
    },
    "night": {
      "description": "Foggy",
      "image": "fog-night.png"
    }
  },
  "48": {
    "day": {
      "description": "Rime Fog",
      "image": "extreme-day-fog.png"
    },
    "night": {
      "description": "Rime Fog",
      "image": "extreme-night-fog.png"
    }
  },
  "51": {
    "day": {
      "description": "Light Drizzle",
      "image": "drizzle.png"
    },
    "night": {
      "description": "Light Drizzle",
      "image": "drizzle.png"
    }
  },
  "53": {
    "day": {
      "description": "Drizzle",
      "image": "partly-cloudy-day-drizzle.png"
    },
    "night": {
      "description": "Drizzle",
      "image": "partly-cloudy-night-drizzle.png"
    }
  },
  "55": {
    "day": {
      "description": "Heavy Drizzle",
      "image": "overcast-day-drizzle.png"
    },
    "night": {
      "description": "Heavy Drizzle",
      "image": "overcast-night-drizzle.png"
    }
  },
  "56": {
    "day": {
      "description": "Light Freezing Drizzle",
      "image": "extreme-drizzle.png"
    },
    "night": {
      "description": "Light Freezing Drizzle",
      "image": "extreme-drizzle.png"
    }
  },
  "57": {
    "day": {
      "description": "Freezing Drizzle",
      "image": "extreme-day-drizzle.png"
    },
    "night": {
      "description": "Freezing Drizzle",
      "image": "extreme-night-drizzle.png"
    }
  },
  "61": {
    "day": {
      "description": "Light Rain",
      "image": "partly-cloudy-day-rain.png"
    },
    "night": {
      "description": "Light Rain",
      "image": "partly-cloudy-night-rain.png"
    }
  },
  "63": {
    "day": {
      "description": "Rain",
      "image": "overcast-day-rain.png"
    },
    "night": {
      "description": "Rain",
      "image": "overcast-night-rain.png"
    }
  },
  "65": {
    "day": {
      "description": "Heavy Rain",
      "image": "extreme-day-rain.png"
    },
    "night": {
      "description": "Heavy Rain",
      "image": "extreme-night-rain.png"
    }
  },
  "66": {
    "day": {
      "description": "Light Freezing Rain",
      "image": "partly-cloudy-day-sleet.png"
    },
    "night": {
      "description": "Light Freezing Rain",
      "image": "partly-cloudy-night-sleet.png"
    }
  },
  "67": {
    "day": {
      "description": "Freezing Rain",
      "image": "overcast-day-sleet.png"
    },
    "night": {
      "description": "Freezing Rain",
      "image": "overcast-night-sleet.png"
    }
  },
  "71": {
    "day": {
      "description": "Light Snow",
      "image": "partly-cloudy-day-snow.png"
    },
    "night": {
      "description": "Light Snow",
      "image": "partly-cloudy-night-snow.png"
    }
  },
  "73": {
    "day": {
      "description": "Snow",
      "image": "overcast-day-snow.png"
    },
    "night": {
      "description": "Snow",
      "image": "overcast-night-snow.png"
    }
  },
  "75": {
    "day": {
      "description": "Heavy Snow",
      "image": "extreme-day-snow.png"
    },
    "night": {
      "description": "Heavy Snow",
      "image": "extreme-night-snow.png"
    }
  },
  "77": {
    "day": {
      "description": "Snow Grains",
      "image": "snowflake.png"
    },
    "night": {
      "description": "Snow Grains",
      "image": "snowflake.png"
    }
  },
  "80": {
    "day": {
      "description": "Light Showers",
      "image": "partly-cloudy-day-rain.png"
    },
    "night": {
      "description": "Light Showers",
      "image": "partly-cloudy-night-rain.png"
    }
  },
  "81": {
    "day": {
      "description": "Showers",
      "image": "overcast-day-rain.png"
    },
    "night": {
      "description": "Showers",
      "image": "overcast-rain.png"
    }
  },
  "82": {
    "day": {
      "description": "Heavy Showers",
      "image": "extreme-day-rain.png"
    },
    "night": {
      "description": "Heavy Showers",
      "image": "extreme-night-rain.png"
    }
  },
  "85": {
    "day": {
      "description": "Light Snow Showers",
      "image": "overcast-day-snow.png"
    },
    "night": {
      "description": "Light Snow Showers",
      "image": "overcast-night-snow.png"
    }
  },
  "86": {
    "day": {
      "description": "Snow Showers",
      "image": "extreme-day-snow.png"
    },
    "night": {
      "description": "Snow Showers",
      "image": "extreme-night-snow.png"
    }
  },
  "95": {
    "day": {
      "description": "Thunderstorm",
      "image": "thunderstorms-day.png"
    },
    "night": {
      "description": "Thunderstorm",
      "image": "thunderstorms-night.png"
    }
  },
  "96": {
    "day": {
      "description": "Light Thunderstorms With Hail",
      "image": "thunderstorms-day-overcast-snow.png"
    },
    "night": {
      "description": "Light Thunderstorms With Hail",
      "image": "thunderstorms-night-overcast-snow.png"
    }
  },
  "99": {
    "day": {
      "description": "Thunderstorm With Hail",
      "image": "thunderstorms-day-extreme-snow.png"
    },
    "night": {
      "description": "Thunderstorm With Hail",
      "image": "thunderstorms-night-extreme-snow.png"
    }
  }
}
"""


class LocalIconSet(IconSet):
    """load icons from the local file system"""

    def __init__(self, name:str):
        self.name = name
        super().__init__()


    def load_weather_codes(self) -> dict:
        """load the weather codes"""
        path = Path(self.name, "weather-codes.json")
        return json.loads(read_text(__package__, path))
        #return json.loads(HACK_CODE_JSON)


    def load_image(self, filename:str) -> Image:
        """load the give image"""
        path = Path(self.name, filename)
        data = read_binary(__package__, path)
        log.debug("loading image: %s", path)
        return Image.open(BytesIO(data))


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
