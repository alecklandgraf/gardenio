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
    global weather_start_time
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
    GPIO.output(GPIO_MOISTURE_POWER_PIN, GPIO.HIGH)
    time.sleep(.5)
    reading = GPIO.input(GPIO_MOISTURE_INPUT_PIN)
    # check initial None state
    if reading == garden_state[GPIO_MOISTURE_INPUT_PIN]:
        print "nothing changed"
    elif reading:
        conn.update_status({'moisture': 'Soil dry'})
        garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
        print "Soil Dry"
        # client.messages.create(
        #     to="+{}".format(TO_NUMBER),
        #     from_="+{}".format(FROM_NUMBER),
        #     body="water me"
        # )
    else:
        conn.update_status({'moisture': 'Soil OK!'})
        print "Soil Ok"
        garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
    GPIO.output(GPIO_MOISTURE_POWER_PIN, GPIO.LOW)


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
        update_moisture_reading()


conn = ControlMyPi(
    JABBER_ID,
    JABBER_PASSWORD,
    SHORT_ID,
    FRIENDLY_NAME,
    PANEL_FORM,
    on_control_message
)

# this has to be declared below the callback
# GPIO.add_event_detect(
#     GPIO_MOISTURE_INPUT_PIN,
#     GPIO.BOTH,
#     callback=update_moisture_reading
# )
if conn.start_control():
    try:
        main_loop()
    finally:
        conn.stop_control()
else:
    print("FAILED TO CONNECT")
