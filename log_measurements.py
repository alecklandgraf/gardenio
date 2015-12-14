from chirp import check
from sensor_log import SensorLog
import datetime

while 1:
    temperature, moisture, light = check()
    log = SensorLog(
        sensor_name='home:office:water_cup',
        temperature=temperature,
        moisture=moisture,
        light=light,
        timestamp=datetime.datetime.now()
    )
    try:
        log.save()
    except:
        print "Error logging data"
    print "log {} saved".format(log)
