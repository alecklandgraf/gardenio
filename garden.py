from controlmypi import ControlMyPi
import RPi.GPIO as GPIO
import time
import requests
import os


# MT TABOR, OR
URL = (
    'https://api.forecast.io/forecast/{}/45.5119,-122.5943'
).format(os.environ.get('FORCASTIO_KEY'))

start_time = time.time()
JABBER_ID = os.environ.get('JABBER_ID')
JABBER_PASSWORD = os.environ.get('JABBER_PASSWORD')
SHORT_ID = 'oneled'
FRIENDLY_NAME = 'Raised Bed 1'
MIN_TEMP, MAX_TEMP, DEFAULT_TEMP = 20, 110, 70
PANEL_FORM = [
    [['O']],
    [
        ['S', 'weather', '-'],
        ['G', 'temp', 'temp', DEFAULT_TEMP, MIN_TEMP, MAX_TEMP]
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
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_NUM, GPIO.OUT)

led_state = {GPIO_NUM: False}


def switch_led(state):
    if led_state[GPIO_NUM] != state:
        GPIO.output(GPIO_NUM, state)  # High to glow!
        conn.update_status({'state': 'watering' if state else 'off'})
        led_state[GPIO_NUM] = state
    global start_time
    if (time.time() - start_time) > 120:
        start_time = time.time()
        update_weather()


def on_control_message(conn, key, value):
    if key == 'on_button':
        switch_led(True)
    elif key == 'off_button':
        switch_led(False)


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
    switch_led(True)
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

if conn.start_control():
    try:
        main_loop()
    finally:
        conn.stop_control()
else:
    print("FAILED TO CONNECT")