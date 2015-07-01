from controlmypi import ControlMyPi
import RPi.GPIO as GPIO
import time
import datetime
import requests
import os
from twilio.rest import TwilioRestClient

# MT TABOR, OR
URL = (
    'https://api.forecast.io/forecast/{}/45.5119,-122.5943'
).format(os.environ.get('FORCASTIO_KEY'))


JABBER_ID = os.environ.get('JABBER_ID')
JABBER_PASSWORD = os.environ.get('JABBER_PASSWORD')
SHORT_ID = 'oneled'
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')
client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
ONE_HOUR = 60 * 60

FRIENDLY_NAME = 'Raised Bed 1'
MIN_TEMP, MAX_TEMP, DEFAULT_TEMP = 20, 110, 70
PANEL_FORM = [
    [['O']],
    [
        ['S', 'weather', '-'],
        ['G', 'temp', 'temp', DEFAULT_TEMP, MIN_TEMP, MAX_TEMP],
    ],
    [['C']],
    [['O']],
    [
        ['L', 'soil moisture'],
        ['S', 'moisture', '-'],
    ],
    [['C']],
    [['O']],
    [
        ['L', 'Soaker'],
        ['B', 'on_button', 'On'],
        ['B', 'off_button', 'Off'],
        ['S', 'state', '-'],
    ],
    [['C']],
]

GPIO_VALVE_PIN = 23
GPIO_MOISTURE_INPUT_PIN = 24
GPIO_MOISTURE_POWER_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_VALVE_PIN, GPIO.OUT)
GPIO.setup(GPIO_MOISTURE_POWER_PIN, GPIO.OUT)
GPIO.setup(GPIO_MOISTURE_INPUT_PIN, GPIO.IN)


garden_state = {
    GPIO_VALVE_PIN: True,
    GPIO_MOISTURE_INPUT_PIN: None
}


def switch_led(state):
    """triggered on "on" "off" button press"""
    if garden_state[GPIO_VALVE_PIN] != state:
        GPIO.output(GPIO_VALVE_PIN, state)  # High to glow!
        conn.update_status({'state': 'watering' if state else 'off'})
        garden_state[GPIO_VALVE_PIN] = state


def on_control_message(conn, key, value):
    if key == 'on_button':
        switch_led(True)
    elif key == 'off_button':
        switch_led(False)


def update_moisture_reading(start_time=None, refresh_threshold_sec=ONE_HOUR):
    if start_time and (time.time() - start_time) < refresh_threshold_sec:
        return start_time
    else:
        start_time = time.time()
        now = datetime.datetime.now()
        GPIO.output(GPIO_MOISTURE_POWER_PIN, GPIO.HIGH)
        # tiny delay to let the sensor pull low
        time.sleep(1)
        reading = GPIO.input(GPIO_MOISTURE_INPUT_PIN)
        # check initial None state
        if reading == garden_state[GPIO_MOISTURE_INPUT_PIN]:
            print "{} nothing changed".format(now)
        elif reading:
            conn.update_status({'moisture': 'Soil dry'})
            print "{} Soil Dry".format(now)
            garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
            client.messages.create(
                to="+{}".format(TO_NUMBER),
                from_="+{}".format(FROM_NUMBER),
                body="water me"
            )
        else:
            conn.update_status({'moisture': 'Soil OK!'})
            print "{} Soil Ok".format(now)
            garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
        GPIO.output(GPIO_MOISTURE_POWER_PIN, GPIO.LOW)
        return start_time


def update_weather(start_time=None, refresh_threshold_sec=ONE_HOUR):
    if start_time and (time.time() - start_time) < refresh_threshold_sec:
        return start_time
    else:
        start_time = time.time()
        resp = requests.get(URL)
        if not resp.ok:
            print "error getting weather data", resp.content
            conn.update_status({
                'weather': 'error getting weather data',
                'temp': 30
            })
        else:
            data = resp.json()
            summary = data['currently']['summary']
            temp = data['currently']['temperature']
            conn.update_status({'weather': '{}'.format(summary), 'temp': temp})
        return start_time


def main_loop():
    switch_led(False)
    # run once
    moisture_start = update_moisture_reading()
    weather_start = update_weather()
    while True:
        time.sleep(3)  # Yield for a while but keep main thread running
        moisture_start = update_moisture_reading(start_time=moisture_start)
        weather_start = update_weather(start_time=weather_start)


conn = ControlMyPi(
    JABBER_ID,
    JABBER_PASSWORD,
    SHORT_ID,
    FRIENDLY_NAME,
    PANEL_FORM,
    on_control_message
)

if conn.start_control():
    try:
        main_loop()
    finally:
        conn.stop_control()
else:
    print("FAILED TO CONNECT")
