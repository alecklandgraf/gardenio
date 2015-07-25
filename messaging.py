import os
from twilio.rest import TwilioRestClient
from logging import getLogger, basicConfig

basicConfig()
logger = getLogger(__name__)


TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')

# need a better dispatching mechanism
MESSAGING_SERVICE = os.environ.get('MESSAGING_SERVICE', 'TWILIO')


def send_twilio_message(message, to_number, from_number):
    twilio_sid = os.environ.get('TWILIO_SID')
    twilio_token = os.environ.get('TWILIO_TOKEN')
    if not twilio_sid or not twilio_token:
        logger.error('Twilio token or SID missing from ENV')
        return

    client = TwilioRestClient(twilio_sid, twilio_token)
    client.messages.create(
        to="+{}".format(to_number),
        from_="+{}".format(from_number),
        body=message
    )


def send_message(message, to_number=TO_NUMBER, from_number=FROM_NUMBER):
    if MESSAGING_SERVICE == 'TWILIO':
        send_twilio_message(message, to_number, from_number)
    else:
        logger.error('Invalid messaging service configured')
