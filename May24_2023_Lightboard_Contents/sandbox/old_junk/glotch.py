import board
import busio
from urp import *
from linear_modules import *
import lightboard.display as display
import lightboard.buttons as buttons
import lightboard.widgets as widgets
import time
nano_uart=busio.UART(board.D29, board.D28, baudrate=115200, timeout=1000*(1/115200)) #Make timeout as small as possible without accidently not reading the whole line...


nano_uart_stopwatch=Stopwatch()
NANO_UART_INTERVAL=1/80/2 #How often should we poll the Nano? (It should output a message 80 times a second)

class LoadCellFilter:
	def __init__(self):
		self.soft_tether=SoftTether(10000)
	def __call__(self,value):
		value=self.soft_tether(value)
		return value

class LoadCellCalibration:
	def __init__(self,load_cell):
		self.load_cell=load_cell

		#The following values should be calibrated; they shouldn't actually be 0 and 1 (0 and 1 are just placeholder values here)
		self.grams_per_raw_value=1

	def get_precise_raw_reading(self,message:str):
		countdown_time=7
		countdown_stopwatch=Stopwatch()
		sampling_delay=2 #When you press the button, you wobble the lightwave. Wait till the wobbling is finished before sampling the weight.
		assert sampling_delay<=countdown_time,'The sampling_delay is part of the countdown_time'
		raw_total=0
		raw_count=0

		while countdown_stopwatch.toc()<countdown_time:
			text=message+'\n\nCountdown:\n    '+str(int(countdown_time-countdown_stopwatch.toc()))+' seconds'
			num_lines=text.count('\n')+1
			do_sampling=countdown_stopwatch.toc()>sampling_delay
			colors=[0xFFFFFF]*(num_lines-1)+[0x44FF88 if do_sampling else 0xFF8800]
			if do_sampling:
				raw_total+=self.load_cell.raw_value
				raw_count+=1
			display.set_menu(text.split('\n'),colors=colors)

		return raw_total/raw_count


	def run_calibration(self,grams):
		old_grams_per_raw_value=self.grams_per_raw_value
		#grams represents the weight of the object that we use to calibrate the load cell
		with display.TemporarySetText('Please take all weight off \nload cell '+repr(self.load_cell.name)+'\nThen press green button 1'):
			with buttons.TemporaryMetalButtonLights(0,0,0):
				with buttons.TemporaryGreenButtonLights(1,0,0,0):
					while not buttons.green_1_press_viewer.value:pass
					buttons.green_button_1.light=False

					raw_tare_value=self.get_precise_raw_reading('Please don\'t wobble the lightwave!\nPreparing to calibrate (taring...)\n'+repr(self.load_cell.name))
					display.set_text('Taring complete! Please put your\n'+str(grams)+' gram weight on load cell\n'+repr(self.load_cell.name)+'\nThen press the green button')

					buttons.green_button_1.light=True
					while not buttons.green_1_press_viewer.value:pass
					buttons.green_button_1.light=False

					raw_weighed_value=self.get_precise_raw_reading('Please don\'t wobble the lightwave!\nPreparing to calibrate ('+str(grams)+' grams...)\n'+repr(self.load_cell.name))
					if raw_weighed_value-raw_tare_value==0:
						#This happened once...it crashed the lightboard...
						display.set_text("ERROR: We must abort calibration\nof load cell "+repr(self.load_cell.name)+"\nDivision by 0 error\nraw_weighed_value=raw_tare_value\n%f=%f\nPress metal button to cancel"%(raw_weighed_value,raw_tare_value))
						buttons.metal_button.color=(1,0,0)
						while not buttons.metal_button.value:
							pass
						return

					self.grams_per_raw_value=grams/(raw_weighed_value-raw_tare_value)

					display.set_text('Weighing complete!')
					time.sleep(.5)

					display.set_text('Weighing complete!')
					moving_average=MovingAverage(30)
					buttons.green_button_1.light=True
					while not buttons.green_1_press_viewer.value:
						value=self(self.load_cell.raw_value,raw_tare_value)
						value=moving_average(value)
						tic()
						display.set_text('Now its time to test\n'+repr(self.load_cell.name)+'\n\nTry putting different known weights\non the load cell, and see\nhow accurate it is. When you\nare done, press the green button.\n\nCurrent weight in grams:\n'+str(int(value)))
						print(value) #I have no idea why, but printing value is apparently critical to making sure that the Nano's values are read properly...this is a complete enigma to me.
						toc()
					buttons.green_button_1.light=False

					if widgets.input_yes_no('Are you satisfied with the results?\n(In other words, is it\naccurate enough for you?)'):
						self.save()
						display.set_text('Saved calibration for load cell\n'+repr(self.load_cell.name))
						time.sleep(1)
						return
					else:
						display.set_text('Cancelled calibration for load cell\n'+repr(self.load_cell.name))
						self.grams_per_raw_value=old_grams_per_raw_value

	def __call__(self,raw_value,tare_value=0):
		return (raw_value-tare_value)*self.grams_per_raw_value

	def save(self):
		pass

	def load(self):
		pass









class LoadCell:
	def __init__(self,name:str):
		self.filter=LoadCellFilter()
		self.calibration=LoadCellCalibration(self)
		self._raw_value=0
		self.name=name

	@property
	def raw_value(self):
		refresh()
		return self._raw_value
	
	@raw_value.setter
	def raw_value(self,value):
		self._raw_value=value
		self.filter(value)

	@property
	def raw_filtered_value(self):
		refresh()
		return self.filter.value

	@property
	def value(self):
		refresh()
		return self.filter.value

	def __repr__(self):
		return repr(self.value)

top_left =LoadCell('1: Top Left'    )
top_right=LoadCell('2: Top Right'   )
mid_left =LoadCell('3: Middle Left' )
mid_right=LoadCell('4: Middle Right')
bot_left =LoadCell('5: Bottom Left' )
bot_right=LoadCell('6: Bottom Right')


load_cells=[top_left,top_right,
            mid_left,mid_right,
            bot_left,bot_right]

SILENT_ERRORS=True
last_message=None
raw_weights=[0]*6
raw_imu    =[0]*6
def refresh():
	if nano_uart_stopwatch.toc()<NANO_UART_INTERVAL:
		return
	global last_message,raw_weights,raw_imu
	data = nano_uart.readline()
	if data is not None:
		nano_uart_stopwatch.tic()
		try:
			last_message=data.decode().strip()
			#Should look like:
			#	last_message=">,-178070,-251194,-64062,185960,50025,-168551,0.6081,-0.5267,8.9232,0.0580,0.0112,0.0548,<"
			assert last_message.count(',')==6*2-1+2,'Failed Commacount: '+repr(last_message)#'There should be 12 comma-separated values', otherwise we likely misread the NANO's message
			assert last_message[0]=='>' and last_message[-1]=='<','Failed ><'
		except Exception as e:
			if not SILENT_ERRORS:
				print_error("Nano UART Error:",str(e))
			return #Eager to give up if something goes wrong, which happens occasionally...don't sweat it when it does, we'll get another message in 1/80 seconds from now...
		else:
			try:
				split_message=last_message.split(',')
				new_raw_weights=list(map(int  ,split_message[1:1+6]))
				new_raw_imu    =list(map(float,split_message[1+6:-1]))#This returns 6 numbers, but honesltly I don't know which number correponds to which (and actually, we don't need to - all that matters is that it contains X,Y,Z for both the gyroscope and the accelerometer)
				raw_weights=new_raw_weights
				raw_imu    =new_raw_imu

				for raw_weight,load_cell in zip(raw_weights,load_cells):
					load_cell.raw_value=raw_weight
				print(*load_cells)
				# print([bool(abs(x.raw_value)>10000) for x in load_cells]) 
			except Exception as e:
				if not SILENT_ERRORS:
					print_error("Nano Parsing Error:",str(e))
				return


bot_right.calibration.run_calibration(681)


while True:
	tic()
	# refresh()
	print(bot_right.raw_value)
	# print(*raw_weights)
	# print(3)
	# ptoc()








# 	pass

# class IMU:
# 	pass



# for i in range(129384123):
while True:
	# print(i) 
	try:
		data = nano_uart.readline()
		if data is not None:
			data_string = ''.join([chr(b) for b in data])
			print(data_string, end="")

			# led.value = False
	except Exception as e:
		print(e)

# from time import sleep
# 	print(i)
# 	sleep(1/60)











from urp import *
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn as ADS1115_AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn as Internal_AnalogIn
import tools
import gc
import storage

import lightboard.ribbons as ribbons
import lightboard.neopixels as neopixels
import lightboard.widgets as widgets
import lightboard.transceiver as transceiver
import lightboard.display as display
import lightboard.buttons as buttons
from lightboard.config import config


# if 'weeble wobble wooble' not in config:
# 	print("WOBBLE")
# 	display.set_text("WEEBLE WOBBLE")
# 	time.sleep(1)
# 	config['weeble wobble wooble']="Wowza"

while True:
	option=widgets.input_select(
		['Calibrate','Brightness','Play']+'asodiuf dsoaijf aos ij doi sjdo if siodf  jioio i ioj ijo ijosdijd iojiojsd f sjd'.split(),
		prompt="Please choose new option\n    Old option: "+repr(config['weeble wobble wooble'])+'\n'+repr(config),
		can_cancel=False,
		must_confirm=True)
	if option=='Play':
		break
	elif option=='Brightness':
		widgets.edit_config_int('neopixels brightness')
	elif option=='Calibrate':
		if widgets.input_yes_no("Would you like to calibrate ribbon A?"):
			ribbons.ribbon_a.run_calibration()
		if widgets.input_yes_no("Would you like to calibrate ribbon B?"):
			ribbons.ribbon_b.run_calibration()

# while True:
# 	option=widgets.input_select(
# 		['Hello','World','How','Is','Life','CLEAR']+'asodiuf dsoaijf aosijdoisjdoif siodf  jioio i ioj ijo ijosdijd iojiojsd f sjd'.split(),
# 		prompt="Please choose new option\n    Old option: "+repr(config['weeble wobble wooble'])+'\n'+repr(config),
# 		can_cancel=True,
# 		must_confirm=True)
# 	if option=='CLEAR':
# 		display.set_text('Clearing all config')
# 		time.sleep(.5)
# 		config.clear()
# 	else:
# 		display.set_text('Set weeble to '+option)
# 		time.sleep(.5)
# 		config['weeble wobble wooble']=option


# def lines(i=0):
#     w=45
#     h=12
#     lines=[('-' if i%2 else '*')*w]*h
#     lines.insert(i,'i'*w)
#     return '\n'.join(lines)[:512]

# display.set_text(lines(2))

# while True:
# 	continue
# 	tic()
# 	gc.collect()
# 	print(gc.mem_free())
# 	ptoc()
# 	for i in range(3):
# 		display.set_text(lines(i))



#TODO: Make this into a function somehow so we can then autotune it
note=None
bend_range=48 #Make sure you set your synths in FL studio to accomadate this
alloff=b''.join([midi_note_off(note) for note in range(128)])
fast=False
# midi_note_off=lambda *args:b''

midi_messages_per_second=60

midi_message_state={'notes_off':set()}
def send_state():
	global midi_message_state
	print(midi_message_state)
	message=b''
	if 'pitch_bend' in midi_message_state:
		message+=midi_pitch_bend_from_semitones(midi_message_state['pitch_bend'],-bend_range,bend_range)
	if 'note_on' in midi_message_state:
		messapge+=midi_note_on(midi_message_state['note_on'])
	if 'notes_off' in midi_message_state:
		message+=b''.join([midi_note_off(note) for note in set(midi_message_state['notes_off'])])
	transceiver.send(message,fast=fast)
	midi_message_state={'notes_off':set()}

def note_on(note):
	if 0<=note<=127:
		midi_message_state['note_on']=note
		if note in midi_message_state['notes_off']:
			midi_message_state['notes_off']-={note}

def gate_off(note):
	if 0<=note<=127:
		global midi_message_state
		midi_message_state={'notes_off':midi_message_state['notes_off']|{note}}

def note_off(note):
	if 0<=note<=127:
		midi_message_state['notes_off']|={note}
		if 'note_on' in midi_message_state and midi_message_state['note_on']==note:
			del midi_message_state['note_on']

def pitch_bend(semitones):
	midi_message_state['pitch_bend']=semitones

buttons.set_green_button_lights(0,0,0,0)
buttons.metal_button.color=(0,0,0)

scales=[major_scale,
        natural_minor_scale,
        harmonic_minor_scale,
        blues_scale,
        chromatic_scale]

scale_names=['Major Scale',
             'Natural Minor Scale',
             'Harmonic Minor Scale',
             'Blues Scale',
             'Chromatic Scale']

def switch_scale():
	global current_scale
	scale_index=(scales.index(current_scale)+1)%len(scales)
	current_scale=scales[scale_index]
	display.set_text("Using:\n"+scale_names[scale_index])
switch_scale_button_index=1
switch_scale_button_press_viewer=buttons.green_press_viewers[switch_scale_button_index]
buttons.green_buttons[switch_scale_button_index].light=True

current_scale=chromatic_scale
switch_scale()
neopixels.draw_pixel_colors(current_scale)
neopixels.refresh()

pixel_offset=12#The number of pixels below the start of the ribbon

pixels_per_note=3
last_midi_time=seconds()
position=0
while True:

	reading_a=ribbons.ribbon_a.processed_cheap_single_touch_reading()
	reading_b=ribbons.ribbon_b.processed_cheap_single_touch_reading()
	reading=reading_a
	if reading_b.gate:
		reading=reading_b

	if reading.gate:
		position=reading.value
		value=note_to_pitch(int(position/pixels_per_note),*current_scale,)
		ribbon=reading.ribbon
		assert isinstance(ribbon,ribbons.Ribbon)
		if ribbon.name=='b':#CHOO CHOO
			value+=12#Up a full octave (12 semitones)
		new_note=value
		new_note=int(new_note)
		remainder=value-new_note
		if new_note != note:
			if note is None:
				note_on(new_note)
				pitch_bend(remainder)
				note=new_note
			else:
				if abs(value-note)>bend_range:
					note_on(new_note)
					note_off(note)
					pitch_bend(remainder)
					note=new_note
				else:
					pitch_bend(value-note)
		else:
			pitch_bend(remainder)
	else:
		if note is not None:
			gate_off(note)
			note=None
	if seconds()-last_midi_time>1/midi_messages_per_second:
		last_midi_time=seconds()
		send_state()
		neopixels.draw_pixel_colors(current_scale,position=position,pixels_per_note=pixels_per_note)
		neopixels.refresh()
	if switch_scale_button_press_viewer.value:
		switch_scale()
















# if widgets.input_yes_no("Would you like to calibrate the ribbon?"):
# 	ribbons.ribbon_a.run_calibration()
# #TODO: Make this into a function somehow so we can then autotune it
# note=None
# bend_range=48 #Make sure you set your synths in FL studio to accomadate this
# alloff=b''.join([midi_note_off(note) for note in range(128)])
# fast=False
# # midi_note_off=lambda *args:b''

# midi_messages_per_second=60

# midi_message_state={'notes_off':set()}
# sent_notes=set()#dont try to turn off notes we never ended up turning on...
# def send_state():
# 	global midi_message_state
# 	print(midi_message_state)
# 	message=b''
# 	if 'pitch_bend' in midi_message_state:
# 		message+=midi_pitch_bend_from_semitones(midi_message_state['pitch_bend'],-bend_range,bend_range)
# 	if 'note_on' in midi_message_state:
# 		message+=midi_note_on(midi_message_state['note_on'])
# 		sent_notes|={midi_message_state['note_on']}
# 	if 'notes_off' in midi_message_state:
# 		message+=b''.join([midi_note_off(note) for note in set(midi_message_state['notes_off'])&sent_notes])
# 		sent_notes-=midi_message_state['notes_off']

# 	transceiver.send(message,fast=fast)
# 	midi_message_state={'notes_off':set()}

# def note_on(note):
# 	midi_message_state['note_on']=note
# 	if note in midi_message_state['notes_off']:
# 		midi_message_state['notes_off']-={note}

# def gate_off(note):
# 	global midi_message_state
# 	midi_message_state={'notes_off':midi_message_state['notes_off']|{note}}

# def note_off(note):
# 	midi_message_state['notes_off']|={note}
# 	if midi_message_state['note_on']==note:
# 		del midi_message_state['note_on']

# def pitch_bend(semitones):
# 	midi_message_state['pitch_bend']=semitones

# last_midi_time=seconds()
# while True:
# 	reading=ribbons.ribbon_a.processed_cheap_single_touch_reading()
# 	if reading.gate:
# 		value=reading.value
# 		new_note=int(value)
# 		remainder=value-new_note
# 		if new_note != note:
# 			neopixels.display_dot(new_note)
# 			if note is None:
# 				note_on(new_note)
# 				pitch_bend(remainder)
# 				note=new_note
# 			else:
# 				if abs(value-note)>bend_range:
# 					note_on(new_note)
# 					note_off(note)
# 					pitch_bend(remainder)
# 					note=new_note
# 				else:
# 					pitch_bend(value-note)
# 		else:
# 			pitch_bend(remainder)
# 	else:
# 		if note is not None:
# 			gate_off(note)
# 			note=None
# 	if seconds()-last_midi_time>1/midi_messages_per_second:
# 		last_midi_time=seconds()
# 		send_state()















# if widgets.input_yes_no("Would you like to calibrate the ribbon?"):
# 	ribbons.ribbon_a.run_calibration()

# #TODO: Make this into a function somehow so we can then autotune it
# note=None
# bend_range=48 #Make sure you set your synths in FL studio to accomadate this
# alloff=b''.join([midi_note_off(note) for note in range(128)])
# # midi_note_off=lambda *args:b''
# while True:
# 	tic()
# 	reading=ribbons.ribbon_a.processed_cheap_single_touch_reading()
# 	if reading.gate:
# 		value=reading.value
# 		new_note=int(value)
# 		remainder=value-new_note
# 		if new_note != note:
# 			neopixels.display_dot(new_note)
# 			if note is None:
# 				transceiver.send(midi_note_on(new_note)+midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range))
# 				note=new_note
# 			else:
# 				if abs(value-note)>bend_range:
# 					transceiver.send(midi_note_on(new_note)\
# 						+midi_note_off(note)
# 						+midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range))
# 					note=new_note
# 				else:
# 					transceiver.send(midi_pitch_bend_from_semitones(value-note,-bend_range,bend_range))
# 			ptoc()
# 		else:
# 			transceiver.send(midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range))
# 	else:
# 		if note is not None:
# 			transceiver.send(midi_note_off(note))
# 			# transceiver.send(alloff)
# 			ptoc()
# 			note=None





# while True:
# 	tic()
# 	reading=ribbons.ribbon_a.processed_cheap_single_touch_reading()
# 	if reading.gate:
# 		value=reading.value
# 		new_note=int(value)
# 		remainder=value-new_note
# 		if new_note != note:
# 			neopixels.display_dot(new_note)
# 			if note is None:
# 				transceiver.send(midi_note_on(new_note)+midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range),fast=fast)
# 				note=new_note
# 			else:
# 				if abs(value-note)>bend_range:
# 					transceiver.send(midi_note_on(new_note)+
# 						+midi_note_off(note)
# 						+midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range),fast=fast)
# 					note=new_note
# 				else:
# 					transceiver.send(midi_pitch_bend_from_semitones(value-note,-bend_range,bend_range),fast=fast)
# 			ptoc()
# 		else:
# 			transceiver.send(midi_pitch_bend_from_semitones(remainder,-bend_range,bend_range),fast=fast)
# 	else:
# 		if note is not None:
# 			transceiver.send(midi_note_off(note),fast=fast)
# 			# transceiver.send(alloff,fast=fast)
# 			ptoc()
# 			note=None
