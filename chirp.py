#https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_I2C
from Adafruit_I2C import Adafruit_I2C
from time import sleep, strftime
from datetime import datetime
deviceAddr = 0x20

i2c = Adafruit_I2C( deviceAddr, -1, False )

def check(debug=True):
    """probes chirp via I2C and returns tuple (temp, moisture, and light)
    temp in degrees C
    dry = 311, submerged ~480
    daylight: 10k, dark: 33k
    """
    i2c.write8( deviceAddr, 0x06 )
    sleep(5)

    i2c.write8(deviceAddr, 3)
    sleep(3)
    light = i2c.readU16(4, False)
    temp = i2c.readS16(5, False)/float(10)
    moisture = i2c.readU16(0, False)
    if debug:
        print str(temp) + ":" + str(moisture) + ":" + str(light)
    return (temp, moisture, light)
