from twilio.rest import TwilioRestClient

TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')
client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
