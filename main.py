#!.venv/bin/python
"""
Experiments with dawn, sunset and weather
"""
import asyncio

from requests import get

from astral import LocationInfo
from astral.sun import sun

import python_weather

from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget





# CONSTANTS
TIMEOUT = 2 #seconds
WEATHER_UNITS = python_weather.IMPERIAL
DATE_FORMAT = "%a %b %d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%a %b %d %H:%M"
EMOJI = {
    "dawn": "🌄",
    "sunrise": "🌅",
    "noon": "🌞",
    "sunset": "🌇",
    "dusk": "🌃",
}


def get_my_ip() -> str:
    """Call ipify service to resolve external IP address of current system"""
    return get('https://api.ipify.org', timeout=TIMEOUT).content.decode('utf8').strip()


def get_my_location() -> LocationInfo:
    """Call ipinfo.io service to resolve external IP address and geoloc data"""
    # Could also use ipinfo.io
    # Get the public IP address of the caller
    response = get('https://ipinfo.io', timeout=TIMEOUT).json()
    loc_strs = response.get("loc").split(',') # "loc": "47.6062,-122.3321"
    latitude = float(loc_strs[0])
    longitude = float(loc_strs[1])

    location = LocationInfo(
        response.get("city"),
        response.get("region"),
        response.get("timezone"),
        latitude,
        longitude)
    return location


def get_location(ip_addr: str) -> LocationInfo:
    """Call ipapi to resolve IP address into geographical location"""
    response = get(f'https://ipapi.co/{ip_addr}/json/', timeout=TIMEOUT).json()

    if response.get("error", False): # Need a default value if "error" isn't in the response
        print(f'Response: {response}')
        return None

    location = LocationInfo(
        response.get("city"),
        response.get("region"),
        response.get("timezone"),
        float(response.get("latitude")),
        float(response.get("longitude")))
    return location


async def print_weather(location:LocationInfo) -> None:
    """Look up location's weather with python_weather"""
    # declare the client.
    async with python_weather.Client(unit=WEATHER_UNITS) as client:
        # fetch a weather forecast from a city
        weather = await client.get(location.name)

        # returns the current day's forecast temperature (int)
        print(f"Current {location.name} temperature is: {weather.temperature}")

        # get the weather forecast for a few days
        for daily in weather:
            print(daily)

            # hourly forecasts
            for hourly in daily:
                print(f' --> {hourly!r}')


def load_weather():
    """
    1. Get the IP address
    2. Use the IP address to get the location and timezone
    3. Calculate the sun record for today in the given location
    4. Print the results
    """
    #ip_addr = get_my_ip()
    #city = get_location(ip_addr)
    city = get_my_location()
    if city:
        s = sun(city.observer, tzinfo=city.timezone)

        print(f"Information for {city.name}/{city.region}:")
        for name, time in s.items():
            print(time.strftime(DATETIME_FORMAT) + " " + EMOJI[name] + " " + name)

        asyncio.run(print_weather(city))
    else:
        print(f"Unable to resolve IP address: {city}")


class SunPhases(Widget):
    """Display sun rise and set times"""

    def render(self) -> RenderResult:
        city = get_my_location()
        s = sun(city.observer, tzinfo=city.timezone)

        buffer = f"{city.name} {city.region}\n{s['dawn'].strftime(DATE_FORMAT)}\n"
        for name, time in s.items():
            buffer += f"{EMOJI[name]} {time.strftime(TIME_FORMAT)} {name}\n"

        return buffer

class WeatherApp(App):
    CSS_PATH = "style.tcss"

    """Command Line Weather"""
    def compose(self) -> ComposeResult:
        yield SunPhases()

    def on_button_pressed(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
