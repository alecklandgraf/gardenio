from controlmypi import ControlMyPi
import RPi.GPIO as GPIO
import time
import datetime
import os
from twilio.rest import TwilioRestClient
from weather import update_weather


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
        ['L', 'Currently'],
        ['S', 'weather', '-'],
        ['G', 'temp', 'temp', DEFAULT_TEMP, MIN_TEMP, MAX_TEMP],
    ],
    [['C']],
    [['O']],
    [
        ['L', 'Soil Moisture'],
        ['S', 'moisture', '-'],
    ],
    [['C']],
    [['O']],
    [
        ['L', 'Next reading in'],
        ['S', 'moisture_reading_time', '-'],
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


def get_next_reading(seconds):
    """returns a tuple of (minutes, seconds) from ``seconds``"""
    return (int(seconds / 60), int(seconds % 60))


def switch_led(state):
    """triggered on "on" "off" button press"""
    if garden_state[GPIO_VALVE_PIN] != state:
        GPIO.output(GPIO_VALVE_PIN, state)  # High to glow!
        conn.update_status({'state': 'Watering' if state else 'Off'})
        garden_state[GPIO_VALVE_PIN] = state


def on_control_message(conn, key, value):
    if key == 'on_button':
        switch_led(True)
    elif key == 'off_button':
        switch_led(False)


def update_moisture_reading(start_time=None, refresh_threshold_sec=ONE_HOUR):
    if start_time and (time.time() - start_time) < refresh_threshold_sec:
        seconds_passed = time.time() - start_time
        min, sec = get_next_reading(refresh_threshold_sec - seconds_passed)
        update_string = '{} minutes'.format(min)
        conn.update_status({'moisture_reading_time': update_string})
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
            conn.update_status({'moisture': 'Dry'})
            print "{} Soil Dry".format(now)
            garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
            client.messages.create(
                to="+{}".format(TO_NUMBER),
                from_="+{}".format(FROM_NUMBER),
                body="water me"
            )
        else:
            conn.update_status({'moisture': 'OK'})
            print "{} Soil Ok".format(now)
            garden_state[GPIO_MOISTURE_INPUT_PIN] = reading
        GPIO.output(GPIO_MOISTURE_POWER_PIN, GPIO.LOW)
        return start_time


def callback(payload):
    conn.update_status(payload)


def main_loop():
    switch_led(False)
    # run once
    moisture_start = update_moisture_reading(callback=callback)
    weather_start = update_weather()
    while True:
        time.sleep(3)  # Yield for a while but keep main thread running
        moisture_start = update_moisture_reading(start_time=moisture_start)
        weather_start = update_weather(start_time=weather_start, callback=callback)


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
