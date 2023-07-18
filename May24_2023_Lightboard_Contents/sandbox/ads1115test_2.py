#QUESTION: In continuous mode, is there lag when setting pins on and off?

from urp import *
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
from digitalio import DigitalInOut, Direction, Pull


# Data collection setup
RATE = 860
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.mode = Mode.CONTINUOUS #Disabled because we can't do this :(( big sad. However, if we only want one output it IS possible to use continuous...but I want generalizability...
ads.data_rate = RATE

# Create single-ended input on channel 0

chan = AnalogIn(ads, ADS.P0)
dio=DigitalInOut(board.D15) # Is physically wired to chan
