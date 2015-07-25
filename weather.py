import os
import time
import requests
from logging import getLogger, basicConfig

basicConfig()
logger = getLogger(__name__)
ONE_HOUR = 60 * 60


def _get_weather_url(lat=None, lon=None):
    """gets forcast.io url for given lat, lon or defaults to Portland, OR"""
    if lat is None:
        lat = '45.5119'
    if lon is None:
        lon = '-122.5943'

    url = 'https://api.forecast.io/forecast/{api_key}/{lat},{lon}'.format(
        api_key=os.environ.get('FORCASTIO_KEY'),
        lat=lat,
        lon=lon
    )
    return url


def update_weather(start_time=None, refresh_threshold_sec=ONE_HOUR, callback=None, lat=None, lon=None):
    """Updates the weather from forcast.io for a given lat, lon (defaults to Portland, OR) once per
    refresh_threshold_sec interval.

    `update_weather` can be called any number of times within the `refresh_threshold_sec` but will
    only request from forcast.io if `start_time` is greater than `refresh_threshold_sec`

    Usage:
        start_time = update_weather()  # hits forcast.io
        while True:
            sleep(1)
            start_time = update_weather(start_time=start_time) # noop until 1 hour has passed, then updates


    :param start_time: time (seconds) last ran `update_weather` hit the api
    :param refresh_threshold_sec: number of seconds to wait until hitting the api
    :param callback: function to call in successful, payload like: {'weather': 'sunny', 'temp': 77.3}
    :param lat: latitude as number (defaults to Portland, OR)
    :param lon: longitude as number (defaults to Portland, OR)
    :returns: time.time() if `start_time` is None or `refresh_threshold_sec` > time.time() + `start_time,
    else returns `start_time`
    """
    if start_time and (time.time() - start_time) < refresh_threshold_sec:
        return start_time
    else:
        start_time = time.time()
        resp = requests.get(_get_weather_url(lat, lon))
        if not resp.ok:
            logger.error("error getting weather data: %s", resp.content)
            if callback and callable(callback):
                callback({
                    'weather': 'error getting weather data',
                    'temp': 30
                })
        else:
            data = resp.json()
            summary = data['currently']['summary']
            temp = data['currently']['temperature']
            if callback and callable(callback):
                callback({'weather': '{}'.format(summary), 'temp': temp})
            else:
                logger.info('%s %s', summary, temp)
        return start_time
