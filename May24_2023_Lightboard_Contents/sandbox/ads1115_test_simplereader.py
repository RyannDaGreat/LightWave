from urp import *
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Data collection setup
RATE = 860

# Create the I2C bus with a fast frequency
if 'i2c' not in dir():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

ads = ADS.ADS1115(i2c)
ads.gain=8

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)

# ADC Configuration
# ads.mode = Mode.CONTINUOUS #Disabled because we can't do this :(( big sad. However, if we only want one output it IS possible to use continuous...but I want generalizability...
ads.data_rate = RATE

N=1000
V=[]

def mean(l):
    l=list(l)
    return sum(l)/len(l)

def std(l):
    u=mean(l)
    return mean((x-u)**2 for x in l)**.5

while True:
    v=chan0.value
    V.append(v)
    while len(V)>N:
        del V[0]
    print(v,0,32768)
    # print(v,'\tstd:',std(V),'\tmean:',mean(V))

# 26334/2 = 13167

#The stamdard deviation at 1x is about .6 to .75 (out of , which is about 5x less than the std
# 3.3*32768/26334=4.10626566416 ~= 4.096 (thte 1x amp)
# Therefore, the max for 

#STANDARD DEVIATIONS VS GAIN:
#   1: ?    to 0.80  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
#   2: ?    to 0.87  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
#   4: ?    to 1.16  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
#   8: ?    to 1.82  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
#  16: 2.72 to 3.75