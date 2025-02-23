#!/env/bin/python
"""
Experiments with dawn, sunset and weather
"""
import datetime as dt

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

from requests import get

from astral import LocationInfo
from astral.sun import sun


# CONSTANTS
TIMEOUT = 2 #seconds


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


def get_sun_data(location: LocationInfo, day: dt.date) -> sun:
    """get data about sun's position give a place and date"""
    return sun(location.observer, day, tzinfo=location.timezone)


# daily note:
# contains data associated with a full day
# current conditions will contain records

class DailyRecord:
    """daily record of interesting weather conditions"""
    date: dt.date # represents a local calendar day
    conditions: dict[int, dict] # indexed on 24-hour

    def __init__(self, date: dt.date, location: LocationInfo):
        self.date = date
        self.location = location
        self.conditions = {}


    def add(self, time: dt.datetime, name: str, value):
        """add condition"""
        assert time.day == self.date.day and time.month == self.date.month and time.year == self.date.year

        existing = self.conditions.get(time.hour, None)
        if not existing:
            existing = {}
            self.conditions[time.hour] = existing

        existing[name] = value


    def sun(self):
        """Get data for:
        dawn
        sunrise
        noon
        sunset
        dusk
        """
        return get_sun_data(self.location, self.date)


def get_weather_json(location: LocationInfo) -> dict:
    """Given a location, get the weather for the next 7 days"""
    # https://api.open-meteo.com/v1/forecast
    # ?latitude=47.60&longitude=-122.34
    # based on https://open-meteo.com/en/docs
    #options = "&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    options = "&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code&temperature_unit=fahrenheit"
    tz = f"&timezone={location.timezone}"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}"

    return get(url+options+tz, timeout=TIMEOUT).json()

# Weather notes
# Hourly:
# - apparent_temperature
# - weather_code
# - cloud_cover: cloudy
# - wind_speed_10m: windy
# - precipitation (inches): rainy


def parse_weather(location: LocationInfo, data:dict) -> dict[int,DailyRecord]:
    """parse the weather data"""
    #--- this assumes 'hourly' key
    # response is 7 days with 24 hours each in a flat array
    result: dict[int,DailyRecord] = {}

    # need to break out 7 DailyRecords, 0-indexed by offset from *first* date in
    #for key, units in response['hourly_units'].items():
    start_date = dt.datetime.fromisoformat(data['hourly']['time'][0]).date() # use the first record for start

    for i, time_str in enumerate(data['hourly']['time']):
        hourstamp = dt.datetime.fromisoformat(time_str)
        #hour = hourstamp.hour # assumes 24-hour TZ-based local time
        date = hourstamp.date()
        day_index = date.day - start_date.day
        day_rec = result.get(day_index, None)
        if not day_rec:
            day_rec = DailyRecord(hourstamp.date(), location)
            result[day_index] = day_rec

        for key, units in data['hourly_units'].items():
            if key != 'time':
                value = data['hourly'][key][i]
                value_str = f"{value}{units}"
                day_rec.add(hourstamp, key, value_str)

    return result





def get_weather(location: LocationInfo) -> list[DailyRecord]:
    """Given a location, get the weather for the next 7 days"""
    data = get_weather_json(location)
    return parse_weather(location, data)


class WeatherSession:
    URL = "https://api.open-meteo.com/v1/forecast"
    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)

    def get(self, location: LocationInfo, **params):
        params.update({
	        "latitude": location.latitude,
	        "longitude": location.longitude,
        })
        responses = self.openmeteo.weather_api(self.URL, params=params)
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly() # should be hourly.Variables(i) in order of params['hourly']
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        # data is:
        # rows of ?? date
        # cols of values
        # broken out by Current Daily Hourly Minutely15 SixHourly,
        # each with per-segment value.

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        print(hourly_dataframe)
        return hourly_dataframe



def cli():
    """cli testing without fance graphics"""
    city = get_my_location()

    # sunrise and set
    # s = sun(city.observer, tzinfo=city.timezone)
    # buffer = f"{city.name} {city.region}\n{s['dawn'].strftime(DATE_FORMAT)}\n"
    # for name, time in s.items():
    #     buffer += f"{EMOJI[name]} {time.strftime(TIME_FORMAT)} {name}\n"
    # print(buffer)

    # hourly weather
    #weather = get_weather(city)
    session = WeatherSession()
    weather = session.get(city, hourly="temperature_2m")

    for day in weather:
        print(day.date)
        for hour, attrs in day.conditions.items():
            print(f"{hour}: {attrs}")

    # really want to convert to time:conditions,
    # where conditions is a human-readable map.
    # hourly records are converted into an array of hour [24] in a day.


    #for k,v in weather.items():
    #    buffer += f"> {k}: {v}\n"

    # parse timestamp into 24-hours timeslot
    #dt.datetime.fromisoformat('2019-01-04T16:41:24+02:00')


if __name__ == "__main__":
    cli()
