import usb_midi as m
o=m.ports[1]
from time import sleep
while True:
	o.write(bytes([0x90,0x3c,0x40]))
	sleep(.5)