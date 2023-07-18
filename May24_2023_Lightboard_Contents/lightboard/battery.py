import digitalio
import board
battery=digitalio.DigitalInOut(board.D17)
battery.switch_to_input(pull=digitalio.Pull.UP)
def is_connected():
	return not battery.value