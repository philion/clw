#!/usr/bin/env python
"""Fancy Weather App"""

import datetime as dt
from io import StringIO
import logging

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static, Log  #, Footer,Header
from textual.widget import Widget

from textual_image.widget import Image as AutoImage

from astral import LocationInfo
from astral.sun import sun

from clw.weather import get_my_location, get_weather, DATE_FORMAT, EMOJI, TIME_FORMAT

from .iconset import IconSet, CachedIconSet, LocalIconSet

log = logging.getLogger(__name__)




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
    icons: IconSet = CachedIconSet(LocalIconSet("png"))

    def compose(self) -> ComposeResult:
        """Yields child widgets."""
        if not self.image_type:
            return

        location = get_my_location()
        weather_week = get_weather(location)
        day_idx = 0
        weather = weather_week[day_idx]

        offset = dt.datetime.now().hour

        for i in range(12):
            with Container() as c:
                hour = offset + i

                if hour >= 24:
                    offset = -i # zero current index
                    hour = 0
                    day_idx += 1 # rollover to next day
                    weather = weather_week[day_idx]

                c.border_title = f"{hour}:00"
                yield Static(weather.location.name)

                code = weather.conditions[hour]['weather_code']
                image = self.icons.get_image(code, hour)
                #log.info(f"{hour} {code} -> {image} {self.icons.get_description(code, hour)}")
                yield AutoImage(image, classes="width-auto height-auto")

                desc = self.icons.get_description(code, hour)
                yield Static(desc)

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
        except Exception:
            print("!!! " + self.format(record))


def setup_logging(app:App, log_level:int):
    """setup loggin for the app"""
    handler = TextualLogHandler(app)

    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        format="{asctime} {levelname:<8s} {name:<16} {message}", style='{')

    logging.getLogger().setLevel(log_level)
    # these chatty loggers get set to ERROR regardless
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("textual_image").setLevel(logging.INFO)


def main() -> None:
    """run the weather app"""
    location = get_my_location()

    app = WeatherApp()
    app.image_type = "auto"
    app.location = location

    # setup logging
    setup_logging(app, logging.DEBUG)

    app.run()


if __name__ == "__main__":
    main()
