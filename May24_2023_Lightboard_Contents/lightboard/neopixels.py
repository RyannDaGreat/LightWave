import board
import neopixel_write
import digitalio
from micropython import const
from lightboard.config import config
from urp import *

length=const(125) #Enter the number of neopixels on the lightboard

#First and last are the pixels that are first and last on the ribbon
first=12
last=length-5

pin = digitalio.DigitalInOut(board.D30)
pin.direction = digitalio.Direction.OUTPUT

buffer = bytearray()
def draw(data:bytearray):
	#Manually draw bytes to the neopixel strip
	#This method runs very fast
	buffer[:len(data)]=data

def refresh():
	#Sometimes buffer can be mutated, since buffer is a bytearray
	#TODO: Keep track of old buffer to save a few millis. Only update when the buffer changes.
	neopixel_write.neopixel_write(pin, buffer)

def write(data):
	draw(data)
	refresh()

def draw_fill(r,g,b):
	assert 0<=r<=255 and 0<=g<=255 and 0<=b<=255,'Neopixel color channels must be integers in the range [0,255]'
	draw(bytes([g,r,b]*length)) # For some reason, my neopixels appear to be in g,r,b order instead of r,g,b order...

def display_fill(r,g,b):
	draw_fill(r,g,b)
	refresh()

all_off=bytes([0,0,0]*length)
def turn_off():
	#Turn off all of the LED's
	write(all_off)

def draw_all_off():
	draw(all_off)

class TemporarilyTurnedOff:
	#Meant to be used like this:
	#	with neopixels.TemporarilyTurnedOff():
	#		(do stuff)
	#Because this is an object, it can be nested while remembering all past buffer
	def __enter__(self):
		self.old_data=bytes(buffer)
		turn_off()
	def __exit__(self,*args):
		write(self.old_data)

def assert_is_valid_byte_color(r,g,b):
	assert 0<=r<=255 and 0<=g<=255 and 0<=b<=255,'Neopixel color channels must be integers in the range [0,255]'

def assert_is_valid_index(index):
	assert isinstance(index,int) and 0<=index<length,'%i is an invalid neopixel index. Please choose an int in the range [0,%i]'%(index,length-1)

def draw_line(start,end,r,g,b):
	#draw a line of uniform color from start to end, inclusive, on the neopixel strip
	start=int(start)
	end=int(end)
	start,end=min(start,end),max(start,end)
	assert start<=end
	if end<0 or start>=length:
		return
	end=min(end,length)#Prevent memory errors
	start=max(0,start)
	buffer[start*3:end*3+3]=bytearray([g,r,b])*(end-start+1)

def draw_dot(index,r=63,g=63,b=63):
	index=int(index)
	assert index>=0
	if index>=length:
		return #You'd never be able to see it anyway...
	buffer[index*3:index*3+3]=bytearray([g,r,b])

def display_dot(index,r=63,g=63,b=63):
	draw_all_off()
	draw_dot(index,r,g,b)
	refresh()

def display_line(start,end,r=63,g=63,b=63):
	draw_all_off()
	draw_line(start,end,r,g,b)
	refresh()





################################ HIGH LEVEL FUNCTIONS BELOW #################################
c=[0,.3,.8,5]
old_lightwave_new_colors=[
					(c[3],c[3],c[3]),#5
					(c[1],c[1],c[2]),
					(c[3],c[0],c[0]),#3
					(c[1],c[2],c[1]),
					(c[3],c[3],c[0]),#4
					(c[0],c[3],c[0]),#1
					(c[2],c[1],c[2]),
					(c[0],c[3],c[3]),#6
					(c[2],c[2],c[1]),
					(c[0],c[0],c[3]),#2
					(c[1],c[2],c[2]),
					(c[3],c[0],c[3]),#0
				]
old_lightwave_old_colors=[
					(c[3],c[3],c[3]),#5
					(c[1],c[1],c[2]),
					(c[3],c[0],c[3]),#3
					(c[1],c[2],c[1]),
					(c[3],c[0],c[0]),#4
					(c[3],c[3],c[0]),#1
					(c[2],c[1],c[2]),
					(c[0],c[3],c[0]),#6
					(c[2],c[2],c[1]),
					(c[0],c[3],c[3]),#2
					(c[1],c[2],c[2]),
					(c[0],c[0],c[3]),#0
				]
semitone_colors=old_lightwave_old_colors

def float_color_to_bytes(r,g,b):
	r=clamp(int(r*256),0,255)
	g=clamp(int(g*256),0,255)
	b=clamp(int(b*256),0,255)
	return bytes([g,r,b])


def draw_pixel_colors(
	scale            = major_scale,
	pixels_per_note  = None,
	num_pixels       = length,
	brightness       = None,
	position         = None, #Assumed to be shifted by pixel_offset
	extra_brightness = 3,
	touch_color      = (1,1,1),
	pixel_offset     = 0,
	used_custom_scale= None):

	#TODO: Simplify this function by taking in a note index and a position index separately.

	import math
	if brightness is None:
		config_brightness=config.get_with_default('neopixels brightness',default=20)
		config_brightness=max(1,config_brightness) #If the config is screwed up and config_brightness is 0, make it 1
		brightness=1/config_brightness
	if pixels_per_note is None:
		pixels_per_note=config.get_with_default('neopixels pixels_per_note',default=3)

	pixels_per_scale = (len(scale)-1)*pixels_per_note #len(scale)-1 because major scale has 8 notes, not 7 (includes 12)

	colors=[semitone_colors[semitone] for semitone in scale[:-1]]
	right_padding=bytes([0,0,0])*int(math.floor((pixels_per_note-1)/2))
	left_padding =bytes([0,0,0])*int(math.ceil ((pixels_per_note-1)/2))
	data=bytearray(b''.join([left_padding+float_color_to_bytes(r*brightness,g*brightness,b*brightness)+right_padding for r,g,b in colors]))

# edit_custom_scale

	def highlight_note(note_index):
		note_index=note_index%(len(scale)-1)
		r,g,b=colors[note_index]

		color_bytes = float_color_to_bytes(
			r*brightness*extra_brightness,
			g*brightness*extra_brightness,
			b*brightness*extra_brightness,
		)

		data_start_index = 3*note_index*pixels_per_note
		data_end_index = data_start_index + 3*pixels_per_note
		data[data_start_index : data_end_index] = color_bytes*pixels_per_note

	if used_custom_scale is not None:
		for note in used_custom_scale:
			highlight_note(note)

	elif position is not None:
		note_index=floor(position/pixels_per_note)
		highlight_note(note_index)


	def circ_shift(array,offset):
		offset%=len(array)
		return array[offset:]+array[:offset]

	data=data*(num_pixels*3//len(data)+2)
	data = circ_shift(data, 3*(pixel_offset%pixels_per_scale))
	
	if position is not None:
		byte_index=floor(position-pixel_offset)*3
		if byte_index>=0 and byte_index<=len(data)-3:
			#Make the individual pixel we're touching glow
			data[byte_index:byte_index+3]=float_color_to_bytes(*touch_color)

	draw(data)
	return data