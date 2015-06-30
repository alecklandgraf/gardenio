from controlmypi import ControlMyPi
import RPi.GPIO as GPIO
import time
import requests
import os
from twilio.rest import TwilioRestClient

# MT TABOR, OR
URL = (
    'https://api.forecast.io/forecast/{}/45.5119,-122.5943'
).format(os.environ.get('FORCASTIO_KEY'))

weather_start_time = time.time()
JABBER_ID = os.environ.get('JABBER_ID')
JABBER_PASSWORD = os.environ.get('JABBER_PASSWORD')
SHORT_ID = 'oneled'
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')
client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)

FRIENDLY_NAME = 'Raised Bed 1'
MIN_TEMP, MAX_TEMP, DEFAULT_TEMP = 20, 110, 70
PANEL_FORM = [
    [['O']],
    [
        ['S', 'weather', '-'],
        ['G', 'temp', 'temp', DEFAULT_TEMP, MIN_TEMP, MAX_TEMP],
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

GPIO_NUM = 23
GPIO_INPUT_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_NUM, GPIO.OUT)
GPIO.setup(GPIO_INPUT_PIN, GPIO.IN)


led_state = {GPIO_NUM: True}


def switch_led(state):
    """triggered on "on" "off" button press"""
    if led_state[GPIO_NUM] != state:
        GPIO.output(GPIO_NUM, state)  # High to glow!
        conn.update_status({'state': 'watering' if state else 'off'})
        led_state[GPIO_NUM] = state
    global weather_start_time
    global moisture_start_time
    if (time.time() - weather_start_time) > 5 * 60:
        weather_start_time = time.time()
        update_weather()


def on_control_message(conn, key, value):
    if key == 'on_button':
        switch_led(True)
    elif key == 'off_button':
        switch_led(False)


def update_moisture_reading(channel=None):
    print "updating moisture reading"
    if (GPIO.input(GPIO_INPUT_PIN)):
        conn.update_status({'moisture': 'Soil dry'})
        client.messages.create(
            to="+{}".format(TO_NUMBER),
            from_="+{}".format(FROM_NUMBER),
            body="water me"
        )
    else:
        conn.update_status({'moisture': 'Soil OK!'})


def update_weather():
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


def main_loop():
    switch_led(False)
    # run once
    update_moisture_reading()
    update_weather()
    while True:
        time.sleep(3)  # Yield for a while but keep main thread running


conn = ControlMyPi(
    JABBER_ID,
    JABBER_PASSWORD,
    SHORT_ID,
    FRIENDLY_NAME,
    PANEL_FORM,
    on_control_message
)

# this has to be declared below the callback
GPIO.add_event_detect(
    GPIO_INPUT_PIN,
    GPIO.BOTH,
    callback=update_moisture_reading
)
if conn.start_control():
    try:
        main_loop()
    finally:
        conn.stop_control()
else:
    print("FAILED TO CONNECT")
