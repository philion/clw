#!/usr/bin/env python
"""Fancy Weather App"""

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static #, Footer, Header
from textual.widget import Widget

from textual_image.widget import Image as AutoImage

#from astral import LocationInfo
from astral.sun import sun

from weather import get_my_location, get_weather, DATE_FORMAT, EMOJI, TIME_FORMAT, DailyRecord

TEST_IMAGE = "png/alert-avalanche-danger.png"

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
            align: center middle;
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

        for i in range(12):
            with Container() as c:
                c.border_title = f"{i}"
                yield Static(weather.location.name)
                yield AutoImage(TEST_IMAGE, classes="width-auto height-auto")
                yield Static(str(weather.conditions[i]))


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
