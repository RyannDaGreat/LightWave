import digitalio
from board import *
import time

led = digitalio.DigitalInOut(D17)
led.direction = digitalio.Direction.OUTPUT

wip = digitalio.DigitalInOut(D16)
wip.direction = digitalio.Direction.OUTPUT

from urp import *

# assert False

t=.01
b=True
while True:
    led.value = True
    time.sleep(t)
    led.value = False
    time.sleep(t)
    if toc()>.1:
    	b=not b
    	wip.value=b
    	print('B',b)
    	tic()