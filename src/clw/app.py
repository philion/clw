#!/usr/bin/env python
"""Fancy Weather App"""

import datetime as dt
from io import BytesIO, StringIO
import logging

from PIL import Image
import requests

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static, Log  #, Footer,Header
from textual.widget import Widget

from textual_image.widget import Image as AutoImage

from astral import LocationInfo
from astral.sun import sun

from clw.weather import get_my_location, get_weather, DATE_FORMAT, EMOJI, TIME_FORMAT, weather_icon, TIMEOUT

log = logging.getLogger(__name__)

#TEST_IMAGE = "png/alert-avalanche-danger.png"

# cheap in-memory cache
_item_cache = {}
def _get(key:str):
    return _item_cache.get(key, None)
def _put(key:str, value):
    existing = _item_cache.get(key, None)
    _item_cache[key] = value
    return existing


def image_for_code(code: str, hour: int) -> Image:
    """load an image for the """
    # cheap day-or-night check, fix with real sun rise/set time from daily record
    tod = "day"
    if hour < 6 or hour > 18:
        tod = "night"

    image_url = weather_icon(code, tod)

    image = _get(image_url)
    log.debug(f"checking cache for {image_url}")
    if not image:
        log.debug(f"loading image: {image_url}")
        response = requests.get(image_url, timeout=TIMEOUT)
        content = BytesIO(response.content)
        image = Image.open(content)
        _put(image_url, image)

    return image


class SunPhases(Widget):
    """Display sun rise and set times"""

    def render(self) -> RenderResult:
        city = get_my_location()
        s = sun(city.observer, tzinfo=city.timezone)

        buffer = f"{city.name} {city.region}\n{s['dawn'].strftime(DATE_FORMAT)}\n"
        for name, time in s.items():
            buffer += f"{EMOJI[name]} {time.strftime(TIME_FORMAT)} {name}\n"

        return buffer

class Gallery(Container):
    """Weather gallery, paints 12 hours for the current weather"""

    DEFAULT_CSS = """
    Gallery {
        layout: grid;
        grid-size: 12 1;
        Container {
            border: round gray;
            align: center top;
        }
        .width-auto {
            width: auto;
        }
        .height-auto {
            height: auto;
        }
        .width-15 {
            width: 15;
        }
        .height-50pct {
            height: 50%;
        }
        .width-100pct {
            width: 100%;
        }
    }
    """

    image_type: reactive[str | None] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        """Yields child widgets."""
        if not self.image_type:
            return

        location = get_my_location()
        weather_week = get_weather(location)
        weather = weather_week[0]

        offset = dt.datetime.now().hour

        for i in range(12):
            with Container() as c:
                hour = offset + i

                if hour >= 24:
                    offset = -i # zero current index
                    hour = 0
                    weather = weather_week[1] # TODO index

                c.border_title = f"{hour}:00"
                yield Static(weather.location.name)

                code = weather.conditions[hour]['weather_code']
                image = image_for_code(code, hour)
                yield AutoImage(image, classes="width-auto height-auto")

                for item in weather.conditions[hour].values():
                    yield Static(item)


# top level location, date
# Lay out hourly column
# - time of day
# - condition icon
# - condition text
# - temperature block
#
# time: start with now().hour, find offsets for next 12 hours


class WeatherApp(App[None]):
    """Command Line Weather App"""

    CSS = """
    WeatherApp {
    }
    """

    image_type: reactive[str | None] = reactive(None, recompose=True)
    location: LocationInfo

    def compose(self) -> ComposeResult:
        """Yields child widgets."""
        yield Gallery().data_bind(WeatherApp.image_type)
        yield Log(max_lines=10_000, highlight=True)


    def on_click(self) -> None:
        """handle mouse click"""
        self.exit()


    def on_key(self, key) -> None:
        """handle key press"""
        log_widget = self.query_one(Log)
        log_widget.write_line(f"key pressed: {key}")


class TextualLogHandler(logging.Handler):
    """Route logs to internal log panel"""
    def __init__(self, app: App) -> None:
        super().__init__()
        self.app = app


    buffer = StringIO()
    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_widget = self.app.query_one(Log)
            log_entry = self.format(record)
            log_widget.write_line(log_entry)
        except:
            print("!!! " + self.format(record))


def main() -> None:
    """run the weather app"""
    location = get_my_location()

    app = WeatherApp()
    app.image_type = "auto"
    app.location = location

    # setup logging
    handler = TextualLogHandler(app)
    logging.basicConfig(level=logging.DEBUG, handlers=[handler]) # read level from args

    app.run()


if __name__ == "__main__":
    main()
