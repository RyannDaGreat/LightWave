#PINS:
#	ADS1115 A0: Single Touch
#	ADS1115 A1: Double Touch A
#	ADS1115 A2: Double Touch B
#	Teensy 12: WOB-bble: Single Touch Pullup/Pulldown (Alternates between HIGH and LOW)
#	Teensy 11: DUA-l 1: Set to HIGH when reading a dual   touch and LOW when reading a single touch
#	Teensy 10: DUA-l 2: Set to HIGH when reading a dual   touch and LOW when reading a single touch
#	Teensy  9: SIN-gle: Set to HIGH when reading a single touch and LOW when reading a dual   touch
#	Teensy 23: Ribbon : Read this from the teensy's internal ADC instead of the ADS1115 when in DUAL mode and we just want to get the gate value

#SOFTWARE TODO: 
#	Get rid of spikes in dual touch mode.
#		- Calibrate the dual touches to match the single touch so we have compatiable numbers everywhere
#			- This can be done in constant space with histograms and bins that fill up as you slowly move a credit card's edge along the ribbon
#		- When the upper and lower touch move away or to the single touch position at roughly opposite velocities, don't change single touch/dual touch status until they appear to be from two fingers (if single touch isn't moving much but both top and bottom dual touches are it should be a red flag...watch the graph...)

from urp import *
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn as ADS1115_AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn as Internal_AnalogIn

if 'i2c' not in dir():
	i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)# Create the I2C bus with a fast frequency

#I2C addresses for ADS1115's: 0x48 and 0x4a for Ribbon A and Ribbon B respectively
ads = ADS.ADS1115(i2c,address=0x4a) 

ads.data_rate = 860 #Maximum frequency of ADS1115 in Hz

ads_gain_single=1
ads_gain_dual  =8 #Uses 100kΩ
ads.gain=ads_gain_single #Change this depending on whether you're measuring dual or single

ads_a0 = ADS1115_AnalogIn(ads, ADS.P0)
ads_a1 = ADS1115_AnalogIn(ads, ADS.P1)
ads_a2 = ADS1115_AnalogIn(ads, ADS.P2)
ads_single=ads_a0
ads_dual_a=ads_a1
ads_dual_b=ads_a2

single_pull=DigitalInOut(board.D32)
single_pin =DigitalInOut(board.D31)
dual_pin_2   =DigitalInOut(board.D25)
dual_pin_1   =DigitalInOut(board.D24)
single_pull.direction=Direction.OUTPUT
single_pin .direction=Direction.OUTPUT
dual_pin_2 .direction=Direction.OUTPUT
dual_pin_1 .direction=Direction.OUTPUT

analog_in = Internal_AnalogIn(board.A13)


def activate_single_transistors():
	single_pin.value=True
	dual_pin_1  .value=False
	dual_pin_2  .value=False

def activate_dual_transistors():
	single_pin.value=False
	dual_pin_1  .value=True
	dual_pin_2  .value=True

class I2CError(OSError):
	pass

class SingleTouchReading:
	GATE_THRESHOLD=500 #This needs to be calibrated after observing the raw_gap when touching and not touching the ribbon. You can do this automatically with some fancy algorithm, or you can just look at the serial monitor while printing reading.raw_gap over and over again

	def __init__(self):
		self.read_raw_lower()
		self.read_raw_upper()
		# print(self.raw_lower,self.raw_upper)
		self.process_readings()
		
	@staticmethod
	def prepare_to_read():
		activate_single_transistors()
		ads.mode=ADS.Mode.SINGLE
		ads.gain=ads_gain_single

	def read_raw_lower(self):
		single_pull.value=False
		self.prepare_to_read()
		try:
			self.raw_lower=ads_single.value
		except OSError as exception:
			raise I2CError(exception)

	def read_raw_upper(self):
		single_pull.value=True
		self.prepare_to_read()
		try:
			self.raw_upper=ads_single.value
		except OSError as exception:
			raise I2CError(exception)

	def process_readings(self):
		self.raw_gap=abs(self.raw_upper-self.raw_lower)
		self.gate=self.raw_gap<self.GATE_THRESHOLD
		self.raw_value=(self.raw_upper+self.raw_lower)/2

class ContinuousSingleTouchReading(SingleTouchReading):
	#Should be similar to SingleTouchReading, but much faster when not using DualTouchReading
	#WARNING AND TODO: This function isn't currently doing enough to flush out anything. Perhaps continous can use the CheapSingleTouchReading's gate, and a single non-wobbling single_pull value
	@staticmethod
	def prepare_to_read():
		activate_single_transistors()
		ads.mode=ADS.Mode.CONTINUOUS
		ads.gain=ads_gain_single
		ads_single.value #Flush out the current reading of the ADC, in-case we changed single_pull in the middle of the ADS's reading (which happens 99% of the time if we don't do this lol - making detecting the gate practically useless)

class CheapSingleTouchReading(SingleTouchReading):
	#TODO: The Teensy's internal ADC is wonked. Between around raw values 30000 and 35000, it jumps (whereas the ADS1115 doesn't jump).
	#		Calibration with respect to the ADS1115's non-cheap single touch should mitigate this problem
	#		Even though the raw range is the same for both analog_in and ads_single, we need a larger GATE_THRESHOLD for CheapSingleTouchReading beacause of this flaw in Teensy's ADC.
	#Uses the Teensy's internal ADC that can read up to 6000x per second
	#TODO: Implement a variation of the SingleTouchReading class called quick-gate check via the Teensy's internal ADC to save a bit of time and get more accurate results on the dual touch readings (because then we can check both upper and lower both before and after the dual readings which means less spikes)
	GATE_THRESHOLD=5000
	def read_raw_lower(self):
		self.prepare_to_read()
		single_pull.value=False
		self.raw_lower=analog_in.value

	def read_raw_upper(self):
		self.prepare_to_read()
		single_pull.value=True
		self.raw_upper=analog_in.value

class DualTouchReading:
	@staticmethod
	def prepare_to_read():
		activate_dual_transistors()
		ads.gain=ads_gain_dual

	def __init__(self):
		DualTouchReading.prepare_to_read()
		try:
			self.raw_a=ads_dual_a.value
			self.raw_b=ads_dual_b.value
		except OSError as exception:
			raise I2CError(exception)


class Squelcher:
	def __init__(self,callable,value=None,error=None,exception_class=Exception):
		#Interfaces like a linear module but can take more than just number classes
		self.callable=callable
		self.error=error
		self.value=value
		self.exception_class=exception_class
	def __call__(self):
		self.error=None
		try:
			self.value=self.callable()
		except self.exception_class as error:
			self.error=error
		return self.value

#These LinearModule-like classes are all callable when inputting a new value, and all store a 'value' parameter to get the last calulated value 
#It's supposed to be pythonic; as opposed to jWave (which implicitly creates a tree). This is more like pytorch than tensorflow...let's see how it goes. 
class Tether:
	def __init__(self,size=1,value=None):
		self.size=size
		self.value=value
	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			self.value=clamp(self.value,value-self.size,value+self.size)
		return self.value

class SoftTether:
	#Acts similar to Tether, but has nicer properties (is smoother, and large jumps cause near-perfect centering for example)
	def __init__(self,size=1,value=None):
		self.size=size
		self.value=value
	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			alpha=1-2.718**(-((value-self.value)/self.size)**2)
			self.value=alpha*value+(1-alpha)*self.value
		return self.value

class Legato:
	def __init__(self,alpha,value=None):
		self.value=value
		self.alpha=alpha
	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			self.value=self.alpha*value+self.value*(1-self.alpha)
		return self.value

class Differential:
	#TODO: Make a version of this class that takes time into account?
	def __init__(self,prev=None,value=None):
		self.prev=prev
		self.value=value
	def __call__(self,value):
		if self.value is None:
			self.prev=value
		self.value=value-self.prev
		self.prev=value
		return self.value

class MovingAverage:
	def __init__(self,length:int):
		#A moving average with 'length' number of samples
		#Todo: To save memory, make a general-purpose sliding window class so that MovingAverage's window can be shared with Delay's window can be shared with MovingMedian's window
		#Todo: Dynamically adjustable length
		assert length>0,'Must have a positive length'
		self.values=[0]*length
		self._length=length
		self._total=0
		self._count=0
		self._cursor=0

	def __call__(self,value):
		self._count=min(self._length,self._count+1)
		self._cursor%=self._length
		self._total-=self.values[self._cursor]
		self.values[self._cursor]=value
		self._total+=value
		self._cursor+=1
		self.value=self._total/self._count
		return self.value

def median(values):
	values=sorted(values)
	length=len(values)
	assert length>0,'Cannot get median of empty list'
	if length%2:
		return  values[length//2]
	else:
		return (values[length//2]+values[length//2-1])/2

class MovingMedian:
	#TODO: Make this more efficient; perhaps use ulab?
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.values=self.values[-self.length:]
		self.value=median(self.values)
		return self.value


	#To be implemented some other time...
	# def __init__(self)

# while True:
	# print(ads_a0.value)

# INTERNAL_DEMO=True
# m=MovingMedian(100)
# activate_single_transistors()
# while True:
# 	# for i in range(100):
# 		# o=m(analog_in.value)
# 	single_pull.value=True
# 	high=analog_in.value
# 	single_pull.value=False
# 	low=analog_in.value
# 	print(m(high-low))




import board
import neopixel_write
import digitalio
import gc
from urp import *
import math

pin = digitalio.DigitalInOut(board.D30)
pin.direction = digitalio.Direction.OUTPUT
numpix=124
pixel_off = bytearray([5, 5, 5]*numpix)
neopixel_write.neopixel_write(pin, pixel_off)

import ulab
from urp import seconds

BRIGHT=10
def get_wav(freq,phase):
	theta=ulab.arange(numpix)/numpix*3.14159*2
	wav=(ulab.vector.sin(theta*freq+phase)+1)/2
	wav=wav**1#(((math.asin(math.sin(seconds()*5))/2)+1)*50+0)
	wav=wav*BRIGHT
	return wav




import board
import digitalio as dio

bmr = dio.DigitalInOut(board.D33)
bmb = dio.DigitalInOut(board.D36)
bmg = dio.DigitalInOut(board.D37)
b4l = dio.DigitalInOut(board.D14)
b3l = dio.DigitalInOut(board.D15)
b2l = dio.DigitalInOut(board.D22)
b1l = dio.DigitalInOut(board.D23)
bmr.switch_to_output()
bmb.switch_to_output()
bmg.switch_to_output()
b4l.switch_to_output()
b3l.switch_to_output()
b2l.switch_to_output()
b1l.switch_to_output()
bmr.value=False
bmb.value=True
bmg.value=True
b4l.value=True
b3l.value=True
b2l.value=True
b1l.value=True


bmo = dio.DigitalInOut(board.D38)
b4o = dio.DigitalInOut(board.D39)
b3o = dio.DigitalInOut(board.D40)
b2o = dio.DigitalInOut(board.D41)
b1o = dio.DigitalInOut(board.D16)
bmo.switch_to_input(pull=dio.Pull.UP)
b4o.switch_to_input(pull=dio.Pull.UP)
b3o.switch_to_input(pull=dio.Pull.UP)
b2o.switch_to_input(pull=dio.Pull.UP)
b1o.switch_to_input(pull=dio.Pull.UP)











"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""
import board
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7789 import ST7789


import digitalio

led = digitalio.DigitalInOut(board.D5)
led.switch_to_output()
led.value=True

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D10
tft_dc = board.D9

display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=board.D6
)

display = ST7789(display_bus, width=320, height=240, rotation=90)

# Make the display context
splash = displayio.Group()
display.show(splash)


# assert False

color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(280, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=20, y=20)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=1, x=57, y=120)
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)








pos=0
while True:
	if toc()>.25:
		text_area.text=str(seconds())
		tic()

	bmr.value=not b4o.value
	bmb.value=not b3o.value
	bmg.value=not b2o.value
	if bmo.value:
		BRIGHT=255
	else:
		BRIGHT=10

	# gc.collect()
	# print('\t++',gc.mem_free())
	r=get_wav(freq=5,phase=seconds()*4)
	g=get_wav(freq=5,phase=seconds()*2)
	b=get_wav(freq=5,phase=seconds()*1)
	wav=ulab.array([r,g,b])
	wav=ulab.array(wav,dtype=ulab.uint8)
	wav=wav.transpose()

	reading=SingleTouchReading()
	if reading.gate:
		pos=numpix-int((reading.raw_value/32000)*numpix)
		print(reading.raw_value)

	if not b4o.value:
		wav[:,0]=0
	if not b3o.value:
		wav[:,1]=0
	if not b2o.value:
		wav[:,2]=0
	wav[pos:,:]=0

	wav=bytearray(wav)
	neopixel_write.neopixel_write(pin, wav)
	ptoc()







CHEAP_DEMO=False
DUAL_DEMO=True
if not DUAL_DEMO:
	CONTINUOUS_MODE=False
	#A really nice single-value reading demo
	single_reader=Squelcher(CheapSingleTouchReading if CHEAP_DEMO else (ContinuousSingleTouchReading if CONTINUOUS_MODE else SingleTouchReading),exception_class=I2CError)
	DISCRETE=True#Set this to true to prove that we really do have 2**15 different spaces on the ribbon (place static object on ribbon to demonstrate)
	#Note that vibrato movement can be detected on a scale EVEN SMALLER than 2**15 resolution
	#Therefore, the total resolution is AT LEAST (750mm/2**15)=23 micrometers=.02mm (holy crap lol - that's 1/5th of the finest 3d printing height I can use...)
	#DISCRETE might be nice when trying to determine if the touch moves (it's nearly 100% accurate from my tests; static objects don't move it at all when DISCRETE=True)
	N=10
	V=[]
	def mean(l):
		l=list(l)
		return sum(l)/len(l)
	def std(l):
		u=mean(l)
		return mean((x-u)**2 for x in l)**.5
	tether=SoftTether(size=5)
	tet2=Tether(1)
	while True:
		single=single_reader()
		if single_reader.error:
			print("ERROR:",single_reader.error)
		else:
			if single.gate:
				V.append(single.raw_value)
				while len(V)>N:
					del V[0]
				val=tether(mean(V))
				if DISCRETE:
					print(tet2(int(val)))
				else:
					print(val)
			else:
				V.clear()
				tether.value=None
else:
	#A really nice Dual-Touch demo that shows the shortcomings of the current processing method
	single_reader=Squelcher(CheapSingleTouchReading if CHEAP_DEMO else SingleTouchReading,exception_class=I2CError)
	dual_reader=Squelcher(DualTouchReading,exception_class=I2CError)
	while True:
		single_before=single_reader()
		dual=dual_reader()
		single_after=single_reader()

		if single_reader.error:
			print("ERROR:",single_reader.error)
		elif dual_reader.error:
			print("ERROR:",dual_reader.error)

		elif single_before.gate and single_after.gate: #TODO: Implement CheapSingleTouchReading so we can run nearly 3x as fast
			print(single_before.raw_value,
				  single_after.raw_value,
				  (single_before.raw_value+single_after.raw_value)/2,
				  dual.raw_a,
				  2**15-dual.raw_b
				  )
