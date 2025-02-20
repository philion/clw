#!/usr/bin/env python
"""Fancy Weather App"""

import datetime as dt
from io import BytesIO

from PIL import Image
import requests

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static  #, Footer,Header
from textual.widget import Widget

from textual_image.widget import Image as AutoImage

#from astral import LocationInfo
from astral.sun import sun

from weather import get_my_location, get_weather, DATE_FORMAT, EMOJI, TIME_FORMAT, weather_icon, TIMEOUT

#TEST_IMAGE = "png/alert-avalanche-danger.png"

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

                image_url = weather_icon(weather.conditions[hour]['weather_code'], hour)
                # NOTE: These need to be cached!
                response = requests.get(image_url, timeout=TIMEOUT)
                content = BytesIO(response.content)
                image = Image.open(content)
                yield AutoImage(image, classes="width-auto height-auto")

                for item in weather.conditions[hour].values():
                    yield Static(item)

                # yield Static(weather.conditions[hour]['temperature_2m'])
                # yield Static(weather.conditions[hour]['temperature_2m'])
                # yield Static(weather.conditions[hour]['relative_humidity_2m'])

# top level location, date
# Lay out hourly column
# - time of day
# - condition icon
# - condition text
# - temperature block
#
# time: start with now().hour, find offsets for next 12 hours



class WeatherApp(App[None]):
    """App showcasing textual-image's image rendering capabilities."""

    CSS = """
    WeatherApp {
    }
    """

    image_type: reactive[str | None] = reactive(None, recompose=True)
    #weather: DailyRecord

    def compose(self) -> ComposeResult:
        """Yields child widgets."""
        #yield Header()
        yield Gallery().data_bind(WeatherApp.image_type)
        #yield Footer()
        #yield SunPhases()


    def on_click(self) -> None:
        """handle mouse click"""
        self.exit()


    def on_key(self, _) -> None:
        """handle key press"""
        self.exit()


def main() -> None:
    """run the weather app"""
    #location = get_my_location()
    #weather_week = get_weather(location)
    app = WeatherApp()
    app.image_type = "auto"
    #app.weather = weather_week[0]
    app.run()


if __name__ == "__main__":
    main()
