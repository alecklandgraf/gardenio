import os
import time
import json

import responses
from unittest2 import TestCase
from weather import _get_weather_url, update_weather


class WeatherTests(TestCase):

    def test__get_weather_url(self):
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
        self.assertEqual(
            _get_weather_url(),
            'https://api.forecast.io/forecast/' + str(os.environ.get('FORCASTIO_KEY')) + '/45.5119,-122.5943')

    @responses.activate
    def tests_update_weather(self):
        def weather_callback(payload):
            self.assertEqual(payload, {'temp': 77, 'weather': 'sunny and meatballs'})

        def request_callback(request):
            resp_body = {'currently': {'summary': 'sunny and meatballs', 'temperature': 77}}
            headers = {}
            return (200, headers, json.dumps(resp_body))
        responses.add_callback(
            responses.GET, _get_weather_url(),
            callback=request_callback,
            content_type='application/json',
        )
        start = time.time()
        start_time = update_weather()
        self.assertLess(start, start_time)
        self.assertLess(start_time, update_weather())
        self.assertEqual(start_time, update_weather(start_time=start_time))
        # this tests the callback
        update_weather(callback=weather_callback)

    @responses.activate
    def tests_update_weather_400(self):
        def weather_callback(payload):
            self.assertEqual(payload, {'temp': 30, 'weather': 'error getting weather data'})

        def request_callback(request):
            resp_body = {'who knows': {'summary': 'sunny and meatballs', 'temperature': 77}}
            headers = {}
            return (400, headers, json.dumps(resp_body))
        responses.add_callback(
            responses.GET, _get_weather_url(),
            callback=request_callback,
            content_type='application/json',
        )

        # this tests the callback
        update_weather(callback=weather_callback)
