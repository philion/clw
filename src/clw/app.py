#!/usr/bin/env python
"""Fancy Weather App"""

import datetime as dt
from io import StringIO
import logging

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static, Log  #, Footer,Header

from textual_image.widget import Image as AutoImage

from astral import LocationInfo

from .weather import WeatherProvider, TIME_FORMAT
from .iconset import IconSet, CachedIconSet, LocalIconSet

log = logging.getLogger(__name__)


# class SunPhases(Widget):
#     """Display sun rise and set times"""

#     def render(self) -> RenderResult:
#         city = get_my_location()
#         s = sun(city.observer, tzinfo=city.timezone)

#         buffer = f"{city.name} {city.region}\n{s['dawn'].strftime(DATE_FORMAT)}\n"
#         for name, timestamp in s.items():
#             buffer += f"{EMOJI[name]} {timestamp.strftime(TIME_FORMAT)} {name}\n"

#         return buffer


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

        provider = WeatherProvider.for_my_location()
        weather_week = provider.get_daily()
        day_idx = 0
        weather = weather_week[day_idx]
        sun = weather.sun.hours()
        offset = dt.datetime.now().hour

        for i in range(12):
            with Container() as c:
                hour = offset + i

                if hour >= 24:
                    offset = -i # zero current index
                    hour = 0
                    day_idx += 1 # rollover to next day
                    weather = weather_week[day_idx]
                    sun = weather.sun.hours()

                title = f"{hour}:00"
                display = weather.location.name
                if hour in sun:
                    # INTENTION
                    # for a given matching hour (0-23),
                    # check if something happens, what it is and what time it happens
                    # so the lookup, based on hour, should return (name,timestamp) tuple
                    name, timestamp = sun[hour]
                    title = timestamp.strftime(TIME_FORMAT)
                    display = name
                    log.info(f"{name} - {title} - {timestamp}")
                c.border_title = title
                yield Static(display)

                code = weather.conditions[hour]['weather_code']
                tod = weather.sun.time_of_day(hour)
                image = self.icons.get_image(code, tod)
                log.info(f"{hour} {code} {tod} -> {image} {self.icons.get_description(code, tod)}")
                yield AutoImage(image, classes="width-auto height-auto")

                desc = self.icons.get_description(code, tod)
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

# Textual Apps
# https://textual.textualize.io/widgets/label/#__tabbed_1_2
# https://github.com/textualize/textual/

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

        if key.key == 'q':
            log_widget.write_line("exiting in 3... 2... 1...")
            self.exit()


class TextualLogHandler(logging.Handler):
    """Route logs to internal log panel"""
    def __init__(self, app: App) -> None:
        super().__init__()
        self.app = app


    buffer = StringIO()
    def emit(self, record: logging.LogRecord) -> None:
        log_widget = self.app.query_one(Log)
        log_entry = self.format(record)
        log_widget.write_line(log_entry)


def setup_logging(app:App, log_level:int):
    """setup loggin for the app"""
    handler = TextualLogHandler(app)

    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        format="{asctime} {levelname:<8s} {name:<16} {message}", style='{')

    logging.getLogger().setLevel(log_level)
    # these chatty loggers get set to ERROR regardless level-10?
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("textual_image").setLevel(logging.INFO)
    logging.getLogger("requests_cache").setLevel(logging.INFO)


def main() -> None:
    """run the weather app"""
    app = WeatherApp()
    app.image_type = "auto"

    # setup logging
    setup_logging(app, logging.DEBUG)

    app.run()


if __name__ == "__main__":
    main()
