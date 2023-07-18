"""CircuitPython Essentials UART Serial example"""
import board
import busio
import digitalio

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.D13)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.D29, board.D28, baudrate=115200)

# for i in range(129384123):
while True:
	# print(i) 
	try:
		data = uart.readline()

		if data is not None:
			led.value = True

			# convert bytearray to string
			data_string = ''.join([chr(b) for b in data])
			print(data_string, end="")

			led.value = False
	except Exception as e:
		print(e)

# from time import sleep
# 	print(i)
# 	sleep(1/60)