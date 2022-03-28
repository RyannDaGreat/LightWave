def millis()->int:
	#Return the global time in milliseconds (returns an integer)
	from time import ticks_ms
	return ticks_ms()



def gtoc()->float:
	#Return time in seconds as a floating point (time.time returns an integer)
	from time import ticks_us
	return ticks_us()/1000000
_global_tic=gtoc()
def tic() -> callable:
	global _global_tic
	_global_tic=local_tic=gtoc()
	def local_toc():  # Gives a permanent toc to this tic, specifically
		return gtoc() - local_tic
	return local_toc  # Returns a method so you can do a=tic();a.toc() ⟵ Gives a local (not global) toc value so each tic can be used as a new timer
def toc() -> float:
	return gtoc() - _global_tic
def ptoc(new_line=True) -> None:
	print(str(toc()) + " seconds",end='\n'if new_line else '')
def ptoctic(label='') -> None:
	print(label,end='')
	ptoc()
	tic()



def unicode_loading_bar(n,chars='▏▎▍▌▋▊▉█'):
    """
    #EXAMPLE 1: for _ in range(200):print(end='\r'+unicode_loading_bar(_));sleep(.05)
    #EXAMPLE 2:
    #    for _ in range(1500):
   	#        import math
   	#        from time import sleep
    #        sleep(1/30)#30fps
    #        tau=6.283185307179586
    #        x=_/1000#_ is between 0 and 1
    #        x**=2#Frequency increases over time
    #        x*=tau
    #        x*=10
    #        x=math.sin(x)
    #        x+=1#Make it all positive
    #        x*=20
    #        x*=8
    #        print(unicode_loading_bar(x))
    #THE ABOVE EXAMPLE PRINTS SOMETHING LIKE THIS:
    # ▊
    # █▊
    # ███▏
    # ████▌
    # ██████▏
    # ███████▊
    # █████████▍
    # ██████████▋
    # ███████████▋
    # ████████████▎
    # ████████████▌
    # ████████████▍
    # ███████████▊
    # ██████████▊
    # █████████▍
    # ███████▉
    # ██████▏
    # ████▋
    # ███
    # █▊
    # ▊
    # ▎
    # ▏
    # ▍
    # █
    # ██
    # ███▎
    """

    assert n>=0,'Input assumption'
    assert isinstance(chars,str),'Input assumption'
    assert len(chars)>=1,'Input assumption'
    n=int(n)
    n=max(0,n)#Clip off negative numbers
    size=len(chars)
    output =n//size*chars[-1]
    output+=chars[n%size]
    return output

def run_as_new_thread(function,*args,**kwargs):
	from _thread import start_new_thread
	start_new_thread(function,args,kwargs)


from machine import I2C, Pin, Timer
import ads1x15_r
addr = 72 #A0. addr is connected to ground. 72=0x48. See the adafruit website.
gain = 1
i2c = I2C(scl=Pin(15), sda=Pin(2), freq=400000)#Multiple ads1115 boards can be connected to the same i2c
ads = ads1x15_r.ADS1115(i2c, addr, gain)
rib1=Pin(4,Pin.OUT)
rib1.value(1)#Set the ribbon's high 
rib2=Pin(16,Pin.OUT)
rib2.value(0)#Set the ribbon's low
# while True:
# 	from time import

# 	print(ads.read())

tic();v=ads.read(7);ptoc();print(v)


def adsread():
	# tic()
	ads.read_request(rate=7, channel1=0, channel2=None)#rate=7 is the fastest. About 200 times per second.
	while not ads.read_ready():
		pass
		# print("READING...")
	out=ads.read_value()
	# ads.read_request(rate=7, channel1=0, channel2=None)#Prepare for the next read ahead of time...
	# ptoc()
	return out

def adsreads(secs=1):
	tic()
	while(toc()<secs):
		n=adsread()
		print(adsread())


def rib(v1=1,v2=0):
	rib1.value(v1)
	rib2.value(v2)

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()

rib(1,0)
adsreads()
rib(0,1)
adsreads()
rib(0,0)
adsreads()
rib(1,1)
adsreads()








class Sensor:
	def read(self):
		#Not making this a property, because I don't want to syntactically disguise
		#the extra CPU this function might go through to get it's sensor reading
		assert False,'This method is abstract'

class Adc(Sensor):
	def read(self):
		assert False,'This method is abstract and returns a float'

class Ads1115(Adc):
	def __init__(self,
				):
		from ads1x15_r import ADS1115#This Ads1115 class is a wrapper around that ADS1115 class
		from machine   import I2C, Pin

		scl_pin=Pin(scl_pin_number)
		sda_pin=Pin(sda_pin_number)
		i2c = I2C(scl=scl_pin, sda=sda_pin, freq=400000)

		addr = 72 #A0. addr is connected to ground. 72=0x48. See the adafruit website.
		gain = 1 #This might be changed. See the documentation.

		self.ads1115=ADS1115(i2c, addr, gain)

	def read(self):
		return self.ads1115.read(rate=7)


class ActiveSingleTouchRibbonADS1115:
	def __init__(self,
				ribbon_vcc_pin_number   :int=16,#The other ribbon pins should be connected to the ADS1115 (the middle pin) and Ground (the other pin)
				ads1115_scl_pin_number  :int= 2,
				ads1115_sda_pin_number  :int=15,#Default numbers are arbitrary suggestions. Might remove them in the future.
				ads1115_alert_pin_number:int= 0,#This implementation needs to use the alert pin
				):

		from ads1x15_r import ADS1115
		from machine import Pin

		addr = 72 #A0. addr is connected to ground. 72=0x48. See the adafruit website.
		gain = 1 #This might be changed depending on the volate input source I use. See the documentation.
		rate = 7#The fastest measurement speed. Can be 0,1,2,3,4,5,6 or 7

		alert_pin=Pin(ads1115_alert_pin_number)
		scl_pin  =Pin(scl_pin_number)
		sda_pin  =Pin(sda_pin_number)

		i2c = I2C(scl=scl_pin, sda=sda_pin, freq=400000)
		ads1115=ADS1115(i2c, addr, gain)
		ads1115.conversion_start(rate=rate)

		alert_pin=Pin(alert)

		mode=True
		ribbon_vcc_pin=Pin(ribbon_vcc_pin_number,Pin.OUT)
		ribbon_vcc_pin.value(mode)

		def interrupt(_):
			nonlocal mode
			read=ads1115.alert_read()#The value read (past tense) from the sensor
			if mode:
				self.value=read
			else:
				self.touch=read
			mode=not mode
			ribbon_vcc_pin.value(mode)







	def _set_left(value:bool):
		self.left_pin.value(int(value))

	def _set_right(value:bool):
		self.right.value(int(value))



class ActiveADS1115:
	#This class uses interrupts to constantly poll the value of this ADS1115 in the background of whatever you're doing
	#It does this by using pin interrupts, which are generated by the ADS1115 chip
	def __init__(self,
				scl_pin_number  :int=2,
				sda_pin_number  :int=15,#Default numbers are arbitrary suggestions. Might remove them in the future.
				
				alert_pin_number:int=0
				):
		from ads1x15 import ADS1115#This Ads1115 class is a wrapper around that ADS1115 class
		from machine   import I2C, Pin

		scl_pin=Pin(scl_pin_number)
		sda_pin=Pin(sda_pin_number)
		i2c = I2C(scl=scl_pin, sda=sda_pin, freq=400000)

		addr = 72 #A0. addr is connected to ground. 72=0x48. See the adafruit website.
		gain = 1 #This might be changed. See the documentation.


		self.ads1115=ADS1115(i2c, addr, gain)

		self._mode=True#When mode is True, we set 





	@property
	def is_pressed(self):


	@property
	def value(self):
		#On a scale from 0 to 1


# poop=1
# def f():
# 	from time import sleep
# 	while True and poop:
# 		# sleep(1)
# 		# print("Pony")
# 		ads.read()
# run_as_new_thread(f)
# while True:
# 	ptoctic()