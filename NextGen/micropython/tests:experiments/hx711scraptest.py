from hx711 import Ryan_HX711
h=Ryan_HX711(27,14)
thing=lambda x:print("HELLO",x)
h.set_read_interrupt(thing)


h.set_read_interrupt()



from hx711 import Ryan_HX711
a=h=Ryan_HX711(27,14)
b=h=Ryan_HX711(33,25)
c=h=Ryan_HX711(9,10)
from time import sleep
while True:
	sleep(.1)
	print(a.average,',',b.average,',',c.average)
