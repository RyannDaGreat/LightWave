from urp import *
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Data collection setup
RATE = 860
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)

# ADC Configuration
# ads.mode = Mode.CONTINUOUS #Disabled because we can't do this :(( big sad. However, if we only want one output it IS possible to use continuous...but I want generalizability...
ads.data_rate = RATE

repeats = 0

data = [None] * SAMPLES

start = time.monotonic()


# Read the same channel over and over
do_gain=True
for i in range(SAMPLES):
    if do_gain: ads.gain=1
    data[i] = chan0.value
    if do_gain: ads.gain=2
    data[i] = chan1.value
    if do_gain: ads.gain=4
    data[i] = chan2.value
    # data[i] = chan1.value
    # data[i] = chan2.value
    # Detect repeated values due to over polling
    print(data[i]%32)
    if data[i] == data[i - 1]:
        repeats += 1



end = time.monotonic()
total_time = end - start

rate_reported = SAMPLES / total_time
rate_actual = (SAMPLES - repeats) / total_time
# NOTE: leave input floating to pickup some random noise
#       This cannot estimate conversion rates higher than polling rate

print("Took {:5.3f} s to acquire {:d} samples.".format(total_time, SAMPLES))
print("")
print("Configured:")
print("    Requested       = {:5d}    sps".format(RATE))
print("    Reported        = {:5d}    sps".format(ads.data_rate))
print("")
print("Actual:")
print("    Polling Rate    = {:8.2f} sps".format(rate_reported))
print("                      {:9.2%}".format(rate_reported / RATE))
print("    Repeats         = {:5d}".format(repeats))
print("    Conversion Rate = {:8.2f} sps   (estimated)".format(rate_actual))

tic()
while toc()<20:
	print(	str(chan0.value).center(10),'\t',
			str(chan1.value).center(10),'\t',
			str(chan2.value).center(10),'\t',
		)

