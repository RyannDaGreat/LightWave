import board
import neopixel_write
import digitalio
import gc
from urp import *
import math

pin = digitalio.DigitalInOut(board.D30)
pin.direction = digitalio.Direction.OUTPUT
numpix=124
pixel_off = bytearray([32, 32, 32]*numpix)
neopixel_write.neopixel_write(pin, pixel_off)

import ulab
from urp import seconds

def get_wav(freq,phase):
	theta=ulab.arange(numpix)/numpix*3.14159*2
	wav=(ulab.vector.sin(theta*freq+phase)+1)/2
	wav=wav**20#(((math.asin(math.sin(seconds()*5))/2)+1)*50+0)
	wav=wav*10
	return wav

while True:
	tic()
	# gc.collect()
	# print('\t++',gc.mem_free())
	r=get_wav(freq=5,phase=seconds()*4)
	g=get_wav(freq=5,phase=seconds()*2)
	b=get_wav(freq=5,phase=seconds()*1)
	wav=ulab.array([r,g,b])
	wav=ulab.array(wav,dtype=ulab.uint8)
	wav=wav.transpose()
	wav=bytearray(wav)
	neopixel_write.neopixel_write(pin, wav)
	ptoc()

