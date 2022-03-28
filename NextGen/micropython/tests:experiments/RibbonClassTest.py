
class Ribbon:#ActiveSingleTouchRibbonADS1115
	__slots__=['value','touch']
	def __init__(self,
				ribbon_vcc_pin_number   :int=16,#The other ribbon pins should be connected to the ADS1115 (the middle pin) and Ground (the other pin)
				ads1115_scl_pin_number  :int=15,
				ads1115_sda_pin_number  :int=2,#Default numbers are arbitrary suggestions. Might remove them in the future.
				ads1115_alert_pin_number:int= 0,#This implementation needs to use the alert pin
				):

		from ads1x15 import ADS1115
		from machine import Pin, I2C

		addr = 72 #A0. addr is connected to ground. 72=0x48. See the adafruit website.
		gain = 1 #This might be changed depending on the volate input source I use. See the documentation.
		rate = 4#The measurement rate. Can be 0,1,2,3,4,5,6 or 7. 7 is fastest, 1 is slowest. I think 4 is the slowest possible speed without being too slow for vibrato. (Slower is better: less CPU interrupts)

		alert_pin     =Pin(ads1115_alert_pin_number)
		scl_pin       =Pin(ads1115_scl_pin_number)
		sda_pin       =Pin(ads1115_sda_pin_number)
		ribbon_vcc_pin=Pin(ribbon_vcc_pin_number,Pin.OUT)

		i2c = I2C(scl=scl_pin, sda=sda_pin, freq=400000)
		ads1115=ADS1115(i2c, addr, gain)
		ads1115.conversion_start(rate=rate)

		mode=True
		ribbon_vcc_pin.value(mode)

		def interrupt_handler(_):
			nonlocal mode
			read=ads1115.alert_read()#The value read (past tense) from the sensor
			print(read)
			# if mode:
				# self.value=read
			# else:
				# self.touch=read
			# mode=not mode
			# ribbon_vcc_pin.value(mode)

		alert_pin.irq(handler=interrupt_handler, trigger=Pin.IRQ_RISING)

Ribbon()

# while True:
	# from time import sleep
	# sleep(.05)
	# print("DANDY!")


def pressed():
	from machine import Pin
	Pin()