#########BIG TODO: WAVEBOX: Make eyehooks longer and flip battery inside!
####TODO: Midi controllers: In a mode where the top is dedicated to 8 buttons you hold down, by holding one and usnig the other ribbon to drag it it sends midi cc values and prints the value and name of controler on display and shows bar for percent while dragging. 
####This mode only activates when you hold down metal BEFORE pressing a ribbon, and then interacting with it. You have to press metal again to make it go away, or make your first press a note and not on the midi controls.

##TODO: Song state loading and saving seems a bit borked....debug it.

#Press metal button + green 1 then metal + green 1 (without letting go of metal) while playing to edit midi cc channels
#Midi cc mode:
#	right now the last one just turns off or on median vibrato when selected. Later this should be a controlable amplitude instead. And a less junky UI.
#Metal+green 1 then either green 1,2, or 3 enters a slot which will autosave scale etc
#Green1+green3 will shift scale up or down
#green 1 or green 3 will temporarily shift 1 semitone
#metal + green 2 will change scale
#metal + green 3 will change num pixels per note
#Custom scale mode:
#   use the two ribbons to select or deselect notes from the custom scale
#   hold metal button or green button 2 (either works) to play a note without selecting or deselecting it
#      (metal because who wants to select notes while shifting? nobody lol)
#   holding green 2 then pressing green 1 and green 3 will shift the scale's colors.
#   the display shows you which notes are in the custom scale as you play it, along with how they differ from a major scale

#TODO: It appears that the pressure calibration tare can CHANGE randomly...even in the middle of playing then exiting....investigate!!

from lightboard.config import config
from linear_modules import *
from urp import *
from collections import OrderedDict
import lightboard.buttons as buttons
import lightboard.display as display
import lightboard.neopixels as neopixels
import lightboard.pressure as pressure
import lightboard.ribbons as ribbons
import lightboard.transceiver as transceiver
import lightboard.widgets as widgets
import math

attempt_to_mount()

def jiggle_mod_wheel():
	#Use this to learn the mod wheel in MIDI synths (e.g. FL Studio) 
	with buttons.TemporaryMetalButtonLights(0,1,1):
		while not buttons.metal_press_viewer.value:
			value=math.sin(seconds())
			value=value+1
			value=value/2
			display.set_text("Jiggling Mod Wheel:\n%f\n\nPress metal to exit"%value)
			transceiver.send(midi_mod_wheel_from_float(value),fast=False)

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

	#Debug
	# if len(midi_message_state)>1 or midi_message_state['notes_off']: #Don't spam when theres nothing worth seeing
		# print(midi_message_state)
	
	message=b''
	if 'pitch_bend' in midi_message_state:
		message+=midi_pitch_bend_from_semitones(midi_message_state['pitch_bend'],-bend_range,bend_range)
	if 'note_on' in midi_message_state:
		message+=midi_note_on(midi_message_state['note_on'])
	if 'midi_cc' in midi_message_state:
		for channel,value in midi_message_state['midi_cc'].items():
			message+=midi_cc(channel,value)
	if 'notes_off' in midi_message_state:
		message+=b''.join([midi_note_off(note) for note in set(midi_message_state['notes_off'])])
	# if use_pressure:
	if use_pressure and ('pitch_bend' in midi_message_state or 'notes_off' in midi_message_state) and not 'note_on' in midi_message_state: #Went from 70ms to 50ms delay instead of "if use_pressure"
		message+=midi_mod_wheel_from_float(pressure.get_pressure())
	transceiver.send(message,fast=fast)
	midi_message_state={'notes_off':set()}

def note_on(note):
	note+=semitone_shift
	if 0<=note<=127:
		midi_message_state['note_on']=note
		if note in midi_message_state['notes_off']:
			midi_message_state['notes_off']-={note}

def gate_off(note):
	note+=semitone_shift
	if 0<=note<=127:
		global midi_message_state
		midi_message_state={'notes_off':midi_message_state['notes_off']|{note}}

def note_off(note):
	note+=semitone_shift
	if 0<=note<=127:
		midi_message_state['notes_off']|={note}
		if 'note_on' in midi_message_state and midi_message_state['note_on']==note:
			del midi_message_state['note_on']

def pitch_bend(semitones):
	semitones+=temp_semitone_shift
	if median_based_vibrato_enabled and not buttons.green_button_2.value:
		#If we're not in free-pitch mode (button 2) then use vibrato
		semitones+=median_based_vibrato_shift
	midi_message_state['pitch_bend']=semitones

def midi_control(channel,value):
	#value should be a float between 0 and 1. Channel should be an int between 0 and 127
	assert isinstance(channel,int)
	value=floor(clamp(value*128,0,127))
	if 'midi_cc' in midi_message_state:
		midi_message_state['midi_cc'][channel]=value
	else:
		midi_message_state['midi_cc']={channel:value}

buttons.set_green_button_lights(0,0,0,0)
buttons.metal_button.color=(0,0,0)

# custom_scale=major_scale.copy()

# custom_scale=[0,2,4,5,7,9,11,12]
# custom_scale=[0,2,4,5,7,9,10,11,12]
custom_scale=config.get_with_default('scales custom 0',default=major_scale.copy())


scales=[
	major_scale,
	custom_scale,
	natural_minor_scale,
	harmonic_minor_scale,
	blues_scale,
	chromatic_scale,
]

scale_names=[
	'Major',
	'Custom',
	'Natural Minor',
	'Harmonic Minor',
	'Blues',
	'Chromatic',
]

key_names=[
	'C',
	'C# Db',
	'D',
	'D# Eb',
	'E',
	'F',
	'F# Gb',
	'G',
	'G# Ab',
	'A',
	'A# Bb',
	'B',
]

def switch_scale(silent=False):
	global current_scale, current_scale_name
	scale_index=(scale_names.index(current_scale_name)+1)%len(scales)
	current_scale=scales[scale_index]
	current_scale_name=scale_names[scale_index]
	save_slot()
	if not silent:
		display_state()

use_pressure=False
def display_state():
	extra_text=''
	custom_mode = edit_custom_scale is not None

	if custom_mode:
		extra_text+='EDITING CUSTOM SCALE\nUse ribbons to add or remove notes\nHold green 2 to play notes\n'
		extra_text+="Custom Scale Semitones:\n   %s "%' '.join([str(x) for x in custom_scale])+"\n"
		extra_text+='aka major +['+' '.join(map(str,sorted(set(custom_scale)-set(major_scale))))+'], -['+' '.join(map(str,sorted(set(major_scale)-set(custom_scale))))+']'
		extra_text+='\n'
	if neo_cc_enabled and neo_cc_get_channel() is not None:
		extra_text+='Midi CC %i'%neo_cc_get_channel()+':  '+midi_cc_descriptions[neo_cc_get_channel()]+'   %.3f\n\n'%midi_cc_values[neo_cc_get_channel()]

	text=extra_text
	if not custom_mode: text+="Scale: "+current_scale_name
	text+="\nKey: %i  aka  %s %i"%(semitone_shift,key_names[semitone_shift%12],semitone_shift//12)
	text+="\n\nPixel Offset: %i"%get_pixel_offset()
	text+='\nPixels Per Note: %i'%pixels_per_note
	text+='\n\nPressure: %s   MedVibrato: %s'%(('Yes' if use_pressure else 'No'),('Yes' if median_based_vibrato_enabled else 'No'))
	text+='\n\nSlot Number: %i'%current_slot_num
	if not custom_mode: text+="\n\nScale Semitones:\n   %s "%' '.join([str(x) for x in current_scale])
	text+='\n\nPress all buttons to exit'

	display.set_text(text)


#SETTINGS START:
pixels_per_note=3
pixel_offset=12-pixels_per_note#The number of pixels below the start of the first note
pixel_offset=pixel_offset-12*pixels_per_note
# pixel_offset=24*3
pixel_offset=-12
semitone_shift=0
#SETTINGS END

def get_pixel_offset():
	if pixel_offset_grab_pos is not None:
		return pixel_offset-floor(position)+pixel_offset_grab_pos
	else:
		return pixel_offset

switch_scale_button_index=1
switch_scale_button_press_viewer=buttons.green_press_viewers[switch_scale_button_index]
buttons.green_buttons[switch_scale_button_index].light=True


last_midi_time=seconds()
position=0
shifted_position=position+pixel_offset
temp_semitone_shift=0
temp_slide_value_shift=0
pixel_offset_grab_pos=None
edit_custom_scale=None

median_based_vibrato_shift=0
median_based_vibrato_module=MedianBasedVibrato(3)
median_based_vibrato_amplitude=1#Semitones/pixel
median_based_vibrato_enabled=False
def median_based_vibrato_toggle_enabled():
	global median_based_vibrato_enabled
	median_based_vibrato_enabled=not median_based_vibrato_enabled
	display_state()

gate_timer=Stopwatch()

#Loading and saving slots is good for performances. You have to prep them though.
slots={1:{},2:{},3:{}}
current_slot_num=0
slot_load_mode=False
def get_current_slot():
	names='current_scale current_scale_name semitone_shift pixel_offset pixels_per_note'.split()
	slot={}
	for name in names:
		value = globals()[name]
		if hasattr(value,'copy'):
			value=value.copy()
		slot[name]=value
	return slot

def save_slot(slot_num=None):
	if slot_num is None:
		slot_num=current_slot_num
	slots[slot_num]=get_current_slot()

def load_slot(slot_num=None):
	global current_slot_num
	slot=slots[slot_num]
	for name in slot:
		globals()[name]=slot[name]
	current_slot_num=slot_num
	display_state()


current_scale     =scales     [-1]
current_scale_name=scale_names[-1]
switch_scale(silent=True)
neopixels.draw_pixel_colors(current_scale)
neopixels.refresh()


midi_cc_values={}#OrderedDict() Can't be ordered dict if we save them in config...#Mapping from channel to float
midi_cc_values[ 2]=.5
midi_cc_values[ 3]=.5
midi_cc_values[ 4]=.5
midi_cc_values[ 5]=.5
midi_cc_values[ 6]=.5
midi_cc_values[ 7]=.5
midi_cc_values[ 8]=.5
midi_cc_values[ 9]=.5
midi_cc_values[10]=.5
midi_cc_values[11]=.5
midi_cc_values[12]=.5
midi_cc_values[13]=.5

midi_cc_descriptions={}#OrderedDict()
midi_cc_descriptions[ 2]='PWM'
midi_cc_descriptions[ 3]='Chorus'
midi_cc_descriptions[ 4]='Squareness'
midi_cc_descriptions[ 5]='Reverb'
midi_cc_descriptions[ 6]='Legato'
midi_cc_descriptions[ 7]='Filter'
midi_cc_descriptions[ 8]='Vibrato Amplitude'
midi_cc_descriptions[ 9]='Ugliness'
midi_cc_descriptions[10]='Attack/Release'
midi_cc_descriptions[11]='Volume'
midi_cc_descriptions[12]='Panning'
midi_cc_descriptions[13]='(Unused)'

midi_cc_channels=sorted(midi_cc_descriptions)

def first_half(array):
	return array[:len(array)//2]
def second_half(array):
	return array[len(array)//2:]

#Metal+1 then (hold metal) metal+1 to enable
neo_cc_enabled=False#Are we using the controllers rn? Neo_cc stands for neopixel midi control channel
neo_cc_length=20
neo_cc_start  =neopixels.last - neo_cc_length
neo_cc_end    =neopixels.last
neo_cc_dragger=DraggableValue(
	value=.5,
	min_value=0,
	max_value=1,
	value_per_pos=.05,
	min_pos=neo_cc_start,
	max_pos=neo_cc_end
)
def neo_cc_get_channel():
	if neo_cc_selector.data is None:
		return None
	return midi_cc_channels[neo_cc_selector.data]
#TODO: Make this less ugly lol
neo_cc_selector=SelectableNeopixelRegions()

def neo_cc_on_select(index):
	neo_cc_dragger.set_value(midi_cc_values[midi_cc_channels[index]])
	display_state()

neo_cc_display_timer=Stopwatch()

neo_cc_selector+=NeopixelRegion(neopixels.first+0 ,neopixels.first+3 ,float_hsv_to_float_rgb(h=0/6,v=1/4,s=1/2),data=0,on_select=lambda:neo_cc_on_select(0))
neo_cc_selector+=NeopixelRegion(neopixels.first+3 ,neopixels.first+6 ,float_hsv_to_float_rgb(h=1/6,v=1/4,s=1/2),data=1,on_select=lambda:neo_cc_on_select(1))
neo_cc_selector+=NeopixelRegion(neopixels.first+6 ,neopixels.first+9 ,float_hsv_to_float_rgb(h=2/6,v=1/4,s=1/2),data=2,on_select=lambda:neo_cc_on_select(2))
neo_cc_selector+=NeopixelRegion(neopixels.first+9 ,neopixels.first+12,float_hsv_to_float_rgb(h=3/6,v=1/4,s=1/2),data=3,on_select=lambda:neo_cc_on_select(3))
neo_cc_selector+=NeopixelRegion(neopixels.first+12,neopixels.first+15,float_hsv_to_float_rgb(h=4/6,v=1/4,s=1/2),data=4,on_select=lambda:neo_cc_on_select(4))
neo_cc_selector+=NeopixelRegion(neopixels.first+15,neopixels.first+18,float_hsv_to_float_rgb(h=5/6,v=1/4,s=1/2),data=5,on_select=lambda:neo_cc_on_select(5))
neo_cc_selector+=NeopixelRegion(neopixels.first+18,neopixels.first+21,float_hsv_to_float_rgb(h=6/6,v=1/4,s=1/2),data=5,on_select=lambda:median_based_vibrato_toggle_enabled())
def neo_cc_toggle_enabled():
	global neo_cc_enabled
	neo_cc_enabled=not neo_cc_enabled
def neo_cc_draw():
	if neo_cc_enabled:
		if neo_cc_display_timer.toc()>.3:#Don't update this too frequently, or it will be laggy...
			display_state()#Update the midi cc value on the display
			neo_cc_display_timer.tic()

		neo_cc_selector.draw()
		# channel=midi_cc_channels[neo_cc_selector.data]
		# base_color=(0,0,.1)
		# _color=(0,0,.1)
		# neo_cc_dragger.min_pos

		if neo_cc_selector.data is not None:
			if neo_cc_dragger.dragging:
				foreground=float_hsv_to_byte_rgb(seconds()/3,.75,1)
				background=(32,10,64)
			elif neo_cc_dragger.held:
				foreground=(64,64,64)
				background=(10,64,32)
			else:
				foreground=(64,64,64)
				background=(64,10,32)
			neopixels.draw_line(neo_cc_start,neo_cc_end,*background)
			neopixels.draw_line(neo_cc_start,neo_cc_end-floor(neo_cc_length*(1-neo_cc_dragger.value)),*foreground) 

def get_current_song_state():
	#Get slots, custom scale, midi CC values, instrument
	output={}
	output['current_patch_index']=current_patch_index
	output['slots'              ]=slots              
	output['current_slot_num'   ]=current_slot_num   
	output['midi_cc_values'     ]=midi_cc_values     
	output['custom_scale'       ]=custom_scale       
	return output

def load_song_state(song_state):
	#TODO check to make sure these things are in there so when we add more stuff in the future it doesn't crash
	_current_patch_index=song_state['current_patch_index']
	_slots              =song_state['slots'              ]
	_current_slot_num   =song_state['current_slot_num'   ]
	_midi_cc_values     =song_state['midi_cc_values'     ]
	_custom_scale       =song_state['custom_scale'       ]


	select_patch(_current_patch_index)

	global custom_scale
	custom_scale=_custom_scale

	global slots
	slots=_slots
	load_slot(_current_slot_num)

	for channel,value in _midi_cc_values.items():
		midi_control(channel,value)

current_song_state_name=None

def save_current_song_state():
	#TODO: Make these use individual files instead of saving in the config, that way we can 

	available_names=sorted(config.get_with_default('song_states',{}))
	default_available_names=set('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9'.split())
	available_names+=sorted(set(default_available_names)-set(available_names))

	state=get_current_song_state()

	try:
		name=widgets.input_select(options=available_names,prompt='Saving Song State\nPlease choose a name:',can_cancel=True)
		if not widgets.input_yes_no('Are you sure you want to load:\n'+name+'?'):
			raise KeyboardInterrupt
	except KeyboardInterrupt:
		display.set_text('Cancelled saving song state')
		sleep(.5)
		return

	config['song_states '+name]=state

	global current_song_state_name
	current_song_state_name=name

	display.set_text('Song state saved!')

def load_selected_song_state():
	if 'song_states' not in config:
		config.get_with_default('song_states',{})

	available_names=sorted(config['song_states'])

	if not len(available_names):
		display.set_text('There are no saved song states!\nAborting...')
		sleep(.5)
		return

	try:
		name=widgets.input_select(options=available_names,prompt='Loading Song State\nPlease choose a name:',can_cancel=True)
		if not widgets.input_yes_no('Are you sure you want to save:\n'+name+'?'):
			raise KeyboardInterrupt
	except KeyboardInterrupt:
		display.set_text('Cancelled loading song state')
		sleep(.5)
		return

	state=config.get_with_default('song_states '+name,get_current_song_state())
	load_song_state(state)

	global current_song_state_name
	current_song_state_name=name

	display.set_text('Song state loaded!')
	sleep(.5)


current_patch_index=0 #The default patch number is always 0
def select_patch(index=None):
	if index is not None:
		message=midi_cc(channel=100,value=index)

		#Doing it 4 times just to be sure...maybe this isn't nessecary...but just in case lol
		for _ in range(4):
			transceiver.send(message,fast=fast)
			sleep(.05)

		global current_patch_index
		current_patch_index=index
	else:
		options = OrderedDict()

		options['Synth'  ] = lambda: select_patch( 0)
		options['Classic'] = lambda: select_patch( 1)
		options['Shells' ] = lambda: select_patch( 2)
		options['Copper' ] = lambda: select_patch( 3)
		options['Steel'  ] = lambda: select_patch( 4)
		options['Distort'] = lambda: select_patch( 5)
		options['Brass'  ] = lambda: select_patch( 6)
		options['Sax'    ] = lambda: select_patch( 7)
		options['Anthem' ] = lambda: select_patch( 8)
		options['Stars'  ] = lambda: select_patch( 9)
		options['Flute'  ] = lambda: select_patch(10)
		options['Banjo'  ] = lambda: select_patch(11)
		options['Organ'  ] = lambda: select_patch(12)

		widgets.run_select_subroutine(options,prompt='Select Axoloti Patch:')


while True:
	use_pressure=True
	edit_custom_scale=None #Either None or the index of a custom scale. Right now there's only 1 custom scale but this might change.
	slot_load_mode=False

	while True:
		option=widgets.input_select(
			['Play','Play Without Pressure','Edit Custom Scale','Calibrate Ribbons','Calibrate Pressure','Brightness','Jiggle Mod Wheel','Load Song State','Save Song State','Select Patch'],
			# prompt="Please choose new option\n    Old option: "+repr(config['weeble wobble wooble'])+'\n'+repr(config),
			prompt='\nLightWave - Choose what to do:',
			can_cancel=False,
			must_confirm=False)
		if option=='Load Song State':
			load_selected_song_state()
		if option=='Save Song State':
			save_current_song_state()
		if option=='Select Patch':
			select_patch()
			break
		if option=='Play Without Pressure':
			use_pressure=False
			break
		if option=='Edit Custom Scale':
			edit_custom_scale=0
			current_scale=chromatic_scale
			current_scale_name='Chromatic'
			break
		if option=='Play':
			break
		elif option=='Brightness':
			def preview_brightness():
				neopixels.draw_pixel_colors(current_scale)
				neopixels.refresh()
			widgets.edit_config_int('neopixels brightness',on_update=preview_brightness,min_value=1,exponential=True,message='Neopixel Brightness\nLarger values are dimmer\n')
		elif option=='Calibrate Ribbons':
			ribbons.show_calibration_menu()
		elif option=='Calibrate Pressure':
			pressure.show_calibration_menu()
		elif option=='Jiggle Mod Wheel':
			jiggle_mod_wheel()


	ribbons.ribbon_a.prev_gate=False
	ribbons.ribbon_b.prev_gate=False
	current_ribbon=None

	display_state()

	while True:

		metal_pressed = buttons.metal_press_viewer.value
		green_1_pressed = buttons.green_1_press_viewer.value
		green_2_pressed = buttons.green_2_press_viewer.value
		green_3_pressed = buttons.green_3_press_viewer.value

		# reading_a=ribbons.ribbon_a.processed_cheap_single_touch_reading()
		# reading_b=ribbons.ribbon_b.processed_cheap_single_touch_reading()

		# reading_a=ribbons.ribbon_a.processed_single_touch_reading()
		# reading_b=ribbons.ribbon_b.processed_single_touch_reading()

		reading_a=ribbons.ribbon_a.processed_dual_touch_reading()
		reading_b=ribbons.ribbon_b.processed_dual_touch_reading()

		temp_semitone_shift=0

		#Coordinate which ribbon to use based on which one was last pressed
		old_current_ribbon=current_ribbon
		if not reading_a.gate and not reading_b.gate:
			current_ribbon=None
			gate=False
		else:
			gate=True
			if current_ribbon:
				if reading_a.gate and (not ribbons.ribbon_a.prev_gate or not reading_b.gate): current_ribbon=ribbons.ribbon_a
				if reading_b.gate and (not ribbons.ribbon_b.prev_gate or not reading_a.gate): current_ribbon=ribbons.ribbon_b
			else:
				if reading_a.gate: current_ribbon=ribbons.ribbon_a
				if reading_b.gate: current_ribbon=ribbons.ribbon_b
			if current_ribbon==ribbons.ribbon_a: reading = reading_a
			if current_ribbon==ribbons.ribbon_b: reading = reading_b
			ribbons.ribbon_a.prev_gate=reading_a.gate
			ribbons.ribbon_b.prev_gate=reading_b.gate

		current_ribbon_changed = old_current_ribbon!=current_ribbon

		if current_ribbon_changed and median_based_vibrato_enabled:
			median_based_vibrato_module.clear()

		if gate:
			# ribbons.ProcessedDualTouchReading.TWO_TOUCH_THRESHOLD=0
			# reading.value=reading.new
			reading.value=reading.mid
			delta = reading.new-reading.old
			# delta = reading.new-position
			if reading.num_fingers==2:

				if 0 and abs(delta)<3: #Width of shift vs breaking to new note
					# reading.value=reading.old
					reading.value=position #Hold old position. TODO this totally breaks when pixel_offset!=0 because of the position+=pixel_offset line...
					temp_semitone_shift=sign(delta)
				else:
					reading.value=reading.new

		#Handle loading and saving of slots
		if not gate and not slot_load_mode and (buttons.metal_button.value and green_1_pressed or metal_pressed and buttons.green_button_1.value):#Press them together in any order
			slot_load_mode=True
			buttons.metal_button.color=(0,1,1) #When button is cyan, we're in slot load mode
		elif metal_pressed and slot_load_mode:
			slot_load_mode=False
			buttons.metal_button.color=(0,0,0) #When button is cyan, we're in slot load mode
		elif not buttons.metal_button.value and slot_load_mode and green_1_pressed: load_slot(1);              buttons.metal_button.color=(0,0,0); slot_load_mode=False
		elif not buttons.metal_button.value and slot_load_mode and green_2_pressed: load_slot(2);              buttons.metal_button.color=(0,0,0); slot_load_mode=False
		elif not buttons.metal_button.value and slot_load_mode and green_3_pressed: load_slot(3);              buttons.metal_button.color=(0,0,0); slot_load_mode=False
		elif     buttons.metal_button.value and slot_load_mode and green_1_pressed: neo_cc_toggle_enabled()
		# elif     buttons.metal_button.value and slot_load_mode and green_1_pressed: save_slot(1);load_slot(1); buttons.metal_button.color=(0,0,0); slot_load_mode=False #TODO: Instead of this, make meta-slots - slot sets that are saved in config
		# elif     buttons.metal_button.value and slot_load_mode and green_2_pressed: save_slot(2);load_slot(2); buttons.metal_button.color=(0,0,0); slot_load_mode=False #TODO: Instead of this, make meta-slots - slot sets that are saved in config
		# elif     buttons.metal_button.value and slot_load_mode and green_3_pressed: save_slot(3);load_slot(3); buttons.metal_button.color=(0,0,0); slot_load_mode=False #TODO: Instead of this, make meta-slots - slot sets that are saved in config
		if slot_load_mode and not buttons.metal_button.value: buttons.metal_button.color=(0,1,0)





		if not gate and not buttons.metal_button.value: #Don't accidently shift key
			if   green_3_pressed and buttons.green_button_1.value:
				semitone_shift-=1
				save_slot()
				display_state()
			elif green_1_pressed and buttons.green_button_3.value:
				semitone_shift+=1
				save_slot()
				display_state()

		if not buttons.metal_button.value:
			if edit_custom_scale is None or not buttons.green_button_2.value:
				if buttons.green_button_1.value:
					temp_semitone_shift=1
				if buttons.green_button_3.value:
					temp_semitone_shift=-1
			else:
				#Scale shifting: this was really tricky to get right, but now it's right.
				#You can shift the scale without changing which parts of the ribbon play what note - essentially just shifting colors.
				#However, the tricky part is that it does this without shifting the colors directly and instead modifies the pixel offset, semitone shift and scale all at once
				if green_3_pressed:
					last_note=custom_scale[-2]
					custom_scale[:]=[0]+[x+(12-last_note) for x in custom_scale[:-1]]
					pixel_offset+=pixels_per_note*(12-last_note)
					semitone_shift-=(12-last_note)
					display_state()
				if green_1_pressed:
					first_note=custom_scale[1]
					custom_scale[:]=[x-first_note for x in custom_scale[1:]]+[12]
					pixel_offset-=pixels_per_note*first_note
					semitone_shift+=first_note
					display_state()


		if gate:
			gate_timer.tic()
			position=reading.value
			shifted_position=position+get_pixel_offset()
			value=shifted_position/pixels_per_note
			if buttons.green_button_2.value and edit_custom_scale is None: #When holding down the middle button, bend the notes...
				if not temp_slide_value_shift:
					temp_slide_value_shift=floor(value)-value #This is so the note doesn't change as soon as we press button 2
				value+=temp_slide_value_shift
			else:
				temp_slide_value_shift=0
				value=floor(value)

			if median_based_vibrato_enabled:
				median_based_vibrato_shift = median_based_vibrato_module(position) * median_based_vibrato_amplitude
			
			value=note_to_pitch(value,*current_scale)
			ribbon=reading.ribbon
			assert isinstance(ribbon,ribbons.Ribbon)
			if ribbon.name=='b':#CHOO CHOO
				value+=12#Up a full octave (12 semitones)
			new_note=value
			new_note=floor(new_note)
			remainder=value-new_note

			if neo_cc_enabled:
				if position in neo_cc_selector:
					if current_ribbon.name=='a':
						midi_cc_channels=first_half(sorted(midi_cc_descriptions))
					elif current_ribbon.name=='b':
						midi_cc_channels=second_half(sorted(midi_cc_descriptions))
					neo_cc_selector.select(position,current_ribbon)
				neo_cc_dragger.drag(position)
				if neo_cc_dragger.dragging:
					neo_cc_channel=neo_cc_get_channel()
					midi_cc_values[neo_cc_channel]=neo_cc_dragger.value
					midi_control(neo_cc_channel,neo_cc_dragger.value)

			if new_note != note:
				if note is None:
					note_on(new_note)
					bend=remainder
					note=new_note

					if median_based_vibrato_enabled:
						median_based_vibrato_module.clear()

					if edit_custom_scale is not None and not (buttons.metal_button.value or buttons.green_button_2.value):
						scale_semitone=new_note
						if reading.ribbon==ribbons.ribbon_a:
							#Add a note to the scale
							add_semitone_to_scale(custom_scale,scale_semitone)
							display_state()
						if reading.ribbon==ribbons.ribbon_b:
							#Remove a note from the scale
							remove_semitone_from_scale(custom_scale,scale_semitone)
							display_state()


				else:
					if abs(value-note)>bend_range:
						note_on(new_note)
						note_off(note)
						bend=remainder
						note=new_note
						if median_based_vibrato_enabled:
							median_based_vibrato_module.clear()
					else:
						bend=value-note
			else:
				bend=remainder
			pitch_bend(bend)
		else:
			if median_based_vibrato_enabled:
				median_based_vibrato_module.clear()
				median_based_vibrato_module.value=0#Don't end on a sour note in mid vibrato
				median_based_vibrato_shift=0
				if 'bend' in dir():
					pitch_bend(bend)

			neo_cc_dragger.release()

			if note is not None:
				gate_off(note)
				note=None

		if seconds()-last_midi_time>1/midi_messages_per_second:
			last_midi_time=seconds()
			send_state()
			neopixels.draw_pixel_colors(current_scale,position=shifted_position,pixels_per_note=pixels_per_note,pixel_offset=get_pixel_offset(),used_custom_scale=custom_scale if edit_custom_scale is not None else None)
			neo_cc_draw()
			neopixels.refresh()

		if buttons.metal_button.value and gate:
			#Press metal+button 1 and drag on ribbon to drag pixels
			if pixel_offset_grab_pos is None:
				pixel_offset_grab_pos=floor(position)
			display_state()
		elif pixel_offset_grab_pos is not None:
			pixel_offset=get_pixel_offset()
			pixel_offset_grab_pos=None
			save_slot()
			
		# if not buttons.metal_button.value and switch_scale_button_press_viewer.value and gate_timer.toc()>1/2 and not gate:
		if buttons.metal_button.value and switch_scale_button_press_viewer.value:
			#Must wait 1/2 second after playing to change the scale
			switch_scale()

		if buttons.metal_button.value and green_3_pressed:
			#Must wait 1/2 second after playing to change the scale
			pixels_per_note+=1
			pixels_per_note=pixels_per_note%6
			pixels_per_note=max(1,pixels_per_note)
			save_slot()
			display_state()

		if buttons.green_button_1.value and buttons.green_button_3.value and buttons.metal_button.value:
			#Reset all presses
			buttons.green_1_press_viewer.value
			buttons.green_2_press_viewer.value
			buttons.green_3_press_viewer.value
			buttons.metal_press_viewer.value

			try:note_off(note);send_state()
			except:pass

			try:
				if edit_custom_scale is not None:
					while current_scale_name!='Custom':
						#Switch scale to custom scale. This will be less janky after I implement a switch_scale(scale_name) function
						switch_scale()
					config['scales custom 0']=custom_scale
					display.set_text('Saved custom scale!')
			except:
				if edit_custom_scale is not None:
					display.set_text('FAILED to save custom scale!')
					sleep(.25)

			neopixels.turn_off()

			display.set_text("Entering main menu")
			sleep(.25)
			break
		
			slot_load_mode=False #If we pressed metal and button 1 while trying to exit, we might have set slot_load_mode True
