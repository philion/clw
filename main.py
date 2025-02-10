"""
Experiments with dawn, sunset and weather
"""
import asyncio
import os

from requests import get

from astral import LocationInfo
from astral.sun import sun

import python_weather


# CONSTANTS
TIMEOUT = 2 #seconds
WEATHER_UNITS = python_weather.IMPERIAL
DATE_FORMAT = "%a %b %d %H:%M:%S"
EMOJI = {
    "dawn": "🌄",
    "sunrise": "🌅",
    "noon": "☀️",
    "sunset": "🌇",
    "dusk": "🌃",
}


def get_my_ip() -> str:
    """Call ipify service to resolve external IP address of current system"""
    # Get the public IP address of the caller
    ip = get('https://api.ipify.org', timeout=TIMEOUT).content.decode('utf8')
    return ip


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
  # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=WEATHER_UNITS) as client:
    # fetch a weather forecast from a city
    weather = await client.get(location.name)

    # returns the current day's forecast temperature (int)
    print(weather.temperature)

    # get the weather forecast for a few days
    for daily in weather:
      print(daily)

      # hourly forecasts
      for hourly in daily:
        print(f' --> {hourly!r}')


def main():
    """
    1. Get the IP address
    2. Use the IP address to get the location and timezone
    3. Calculate the sun record for today in the given location
    4. Print the results
    """
    ip_addr = get_my_ip()
    city = get_location(ip_addr)
    if city:
        s = sun(city.observer, tzinfo=city.timezone)

        print(f"Information for {city.name}/{city.region}:\n")
        for name, time in s.items():
            print(time.strftime(DATE_FORMAT) + " " + EMOJI[name] + " " + name)

        asyncio.run(print_weather(city))
    else:
        print(f"Unable to resolve IP address: {ip_addr}")


if __name__ == "__main__":
    main()
