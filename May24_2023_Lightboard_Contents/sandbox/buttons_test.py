import board
import digitalio as dio

bmr = dio.DigitalInOut(board.D33)
bmb = dio.DigitalInOut(board.D36)
bmg = dio.DigitalInOut(board.D37)
b4l = dio.DigitalInOut(board.D14)
b3l = dio.DigitalInOut(board.D15)
b2l = dio.DigitalInOut(board.D22)
b1l = dio.DigitalInOut(board.D23)
bmr.switch_to_output()
bmb.switch_to_output()
bmg.switch_to_output()
b4l.switch_to_output()
b3l.switch_to_output()
b2l.switch_to_output()
b1l.switch_to_output()
bmr.value=False
bmb.value=True
bmg.value=True
b4l.value=True
b3l.value=True
b2l.value=True
b1l.value=True


bmo = dio.DigitalInOut(board.D38)
b4o = dio.DigitalInOut(board.D39)
b3o = dio.DigitalInOut(board.D40)
b2o = dio.DigitalInOut(board.D41)
b1o = dio.DigitalInOut(board.D16)
bmo.switch_to_input(pull=dio.Pull.UP)
b4o.switch_to_input(pull=dio.Pull.UP)
b3o.switch_to_input(pull=dio.Pull.UP)
b2o.switch_to_input(pull=dio.Pull.UP)
b1o.switch_to_input(pull=dio.Pull.UP)



while True:
	print(bmo.value,'\t',b4o.value,'\t',b3o.value,'\t',b2o.value,'\t',b1o.value,'\t',)
	bmr.value=not b4o.value
	bmb.value=not b3o.value
	bmg.value=not b2o.value