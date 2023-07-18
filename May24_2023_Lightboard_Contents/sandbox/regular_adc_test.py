import board
import analogio
adc1 = analogio.AnalogIn(board.A0)
adc2 = analogio.AnalogIn(board.A1)
adc3 = analogio.AnalogIn(board.A2)
from urp import *

tic()
N=10000
for i in range(N):
	_=adc1.value #Somehow it can tell it's not being assigned???
	_=adc2.value
	_=adc3.value
print("TIME",toc(),N/toc(),toc()/N)



# while True:


# 	print(adc.value%16)
# 	print(adc.value%16)
# 	print(adc.value%16)