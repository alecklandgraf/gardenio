import os
import time

from unittest2 import TestCase
from weather import _get_weather_url, update_weather


class WeatherTests(TestCase):

    def test__get_weather_url(self):
        self.assertIn(
            'https://api.forecast.io/forecast/',
            _get_weather_url(),
        )
        self.assertIn(
            '45.5119,-122.5943',
            _get_weather_url(None, None),
        )
        self.assertIn(
            '45.5119,-122.5943',
            _get_weather_url(),
        )
        self.assertIn(
            '45.5119,-122.5943',
            _get_weather_url(lat=None, lon=None),
        )
        self.assertIn(
            str(os.environ.get('FORCASTIO_KEY')),
            _get_weather_url(),
        )
        self.assertIn(
            '45,-122',
            _get_weather_url(45, lon=-122),
        )

    def tests_update_weather(self):
        start = time.time()
        start_time = update_weather()
        self.assertLess(start, start_time)
        self.assertLess(start_time, update_weather())
