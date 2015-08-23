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
        # get a time to start with
        start = time.time()
        # get a new time from update_weather since we didn't pass in start_time
        start_time = update_weather()
        self.assertLess(start, start_time)
        # start_time should be less that the returned time from update_weather
        self.assertLess(start_time, update_weather())
        # passing in a time should return that same time if one hour hasn't passed
        self.assertEqual(start_time, update_weather(start_time=start_time))
        # if our refresh threshold is passed we should get a new start time
        self.assertLess(start, update_weather(start_time=start, refresh_threshold_sec=0.00001))
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
