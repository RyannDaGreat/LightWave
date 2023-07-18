import board
import digitalio as dio

t = dio.DigitalInOut(board.D20)
t.switch_to_input(pull=dio.Pull.UP)



while True:
	print(t.value)