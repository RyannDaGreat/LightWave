#r stands for 'micro-rp'
#This library is originally designed for CircuitPython on my Teensy4.0 and Teensy4.1 boards. If using other implementations or boards, you might need to adapt this code.
#Attempt to make the Teensy's drive space writeable...

read_only=True
def attempt_to_mount():
	import lightboard.battery
	global read_only
	if lightboard.battery.is_connected():
		# import lightboard.display
		# lightboard.display.set_text("BATTERY ON!")
		try:
			#Try to mitigate errors when saving files
			#		open('file.txt','wb')
			#	results in...
			#		OSError: [Errno 30] Read-only filesystem
			import storage
			storage.remount('/', readonly=False)
			read_only=False
			# lightboard.display.set_text("Writeable!")
		except RuntimeError as error:
			#When plugged into USB, this doesn't work - and there's no way to write to the filesystem :\
			#SD cards don't work in the current circuitpython version...
			#	RuntimeError: Cannot remount '/' when USB is active.
			print("Failed to remount:",error)
			pass

# attempt_to_mount() #TODO: When we fix the power issue, we can bring this back to automatic mode. For now, its triggered in a dialog from code.py

import time
import math
from time import sleep
from time import monotonic_ns
from micropython import const
from math import floor,ceil

pi =3.1415926535
tau=2*pi

def millis():
	return monotonic_ns()//1000000

def seconds():
	return monotonic_ns() /1000000000

def print_error(*args):
	print(*args)#This can be disabled if you have to
	pass

def print_warning(*args):
	print(*args)#This can be disabled if you have to
	pass

_toc=0
def gtoc():
	return seconds()
# def toc():
# 	return gtoc()-_toc
# def tic():
# 	global _toc
# 	_toc=gtoc()
# def ptoc(*args):
# 	print(*(args+('%.7f'%toc(),)))
# def ptoctic(*args):
# 	ptoc(*args)
# 	tic()
class Stopwatch:
	def __init__(self):
		self._toc=gtoc()
	def toc(self):
		return gtoc()-self._toc
	def tic(self):
		self._toc=gtoc()
	def ptoc(self,*args):
		print(*(args+('%.7f'%self.toc(),)))
	def ptoctic(*args):
		self.ptoc(*args)
		self.tic()
stopwatch=Stopwatch()
toc=stopwatch.toc
tic=stopwatch.tic
ptoc=stopwatch.ptoc
ptoctic=stopwatch.ptoctic



def clamp(x,a,b):
	return min(max(a,b),max(min(a,b),x))

def midi_note_off(note:int,vel:int=127,chan:int=0):
	assert 0<=note<128
	assert 0<=vel <128
	assert 0<=chan<16
	return bytes([0x80+chan,note,vel])

def midi_all_notes_off():
	return bytes([123,0])

def midi_all_sound_off():
	return bytes([121,0])

def midi_volume(vol:int):
	assert 0<=vol<256
	return bytes([3,vol])

def midi_note_on(note:int,vel:int=127,chan:int=0):
	assert 0<=note<128
	assert 0<=vel <128
	assert 0<=chan<16
	return bytes([0x90+chan,note,vel])

def midi_cc(channel:int,value:int):
	#Midi CC == Midi Continuous Controllers
	#TODO: Support MIDI 2.0
	assert 0<=channel<128
	assert 0<=value<128
	return bytes([176,channel,value])

def midi_mod_wheel(value:int):
	assert 0<=value<128
	return midi_cc(1,value)

def midi_mod_wheel_from_float(value:float):
	value = int(clamp(value*128,0,127))
	return midi_mod_wheel(value)

def float_color_to_byte_color(r,g,b):
	return min(255,floor(r*256)),\
	       min(255,floor(g*256)),\
	       min(255,floor(b*256))

def float_hsv_to_float_rgb(h, s=1, v=1):
	h=h%1
	if s == 0.0: return (v, v, v)
	i = int(h*6.) # XXX assume int() truncates!
	f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
	if i == 0: return (v, t, p)
	if i == 1: return (q, v, p)
	if i == 2: return (p, v, t)
	if i == 3: return (p, q, v)
	if i == 4: return (t, p, v)
	if i == 5: return (v, p, q)

def float_hsv_to_byte_rgb(h, s=1, v=1):
	s=clamp(s,0,1)
	v=clamp(v,0,1)
	return float_color_to_byte_color(*float_hsv_to_float_rgb(h,s,v))

def midi_pitch_bend(coarse:int,fine:int):
	return bytes([224,coarse,fine])

def midi_pitch_bend_from_semitones(semitones,lower=-2,upper=2):
	value=(semitones-lower)/(upper-lower)
	coarse=int(value*128)
	fine=int(value*128**2)%128
	return midi_pitch_bend(clamp(fine,0,255),clamp(coarse,0,255))

def shuffle(array)->None:
	#Mutates an input list such that it's shuffled
	import random
	max_index=len(array)-1
	for index in range(max_index):
		random_index=random.randint(index,max_index)
		array[index],array[random_index] = array[random_index],array[index]

def shuffled(array):
	if isinstance(array,str  ):return ''.join(shuffled(list(array)))
	if isinstance(array,bytes):return bytes(shuffled(list(array))) #Maybe use a memory view to make it faster?
	array=array.copy()
	shuffle(array)
	return array

def save_object_via_umsgpack(object,path):
	import umsgpack
	data=umsgpack.packb(object)

def bytes_to_file(data:bytes,path:str=None):
	assert not read_only,'Filesystem is read-only - make sure CircuitPython isnt connected to a computer via USB'
	assert isinstance(data,bytes)
	assert isinstance(path,str)
	try:
		out=open(path,'wb')
		out.write(data)
	finally:
		out.close()

def file_to_bytes(path:str):
	try:
		out=open(path,'rb')
		data=out.read()
	finally:
		out.close()
	return data

def bytes_to_object(data:bytes):
	import umsgpack
	return umsgpack.unpackb(data)

def object_to_bytes(object):
	import umsgpack
	return umsgpack.packb(object)

def file_to_object(path:str):
	return bytes_to_object(file_to_bytes(path))

def object_to_file(object,path:str):
	return bytes_to_file(object_to_bytes(object),path)

def path_exists(path:str):
	import os
	try:
		os.stat(path)
		return True
	except OSError:
		#OSError: [Errno 2] No such file/directory
		return False

def _path_join(path_a:str,path_b:str):
	#Joins paths together.
	#	EXAMPLES:
	#		path_join('folder' , 'file') --> 'folder/file'
	#		path_join('folder/', 'file') --> 'folder/file'
	#		path_join('folder/','/file') --> 'folder/file'
	#		path_join('folder ','/file') --> 'folder/file'
	if path_a.endswith('/'):
		path_a=path_a[:-1]
	if path_b.startswith('/'):
		path_b=path_b[1:]
	return path_a+'/'+path_b

def path_join(*paths):
	if not len(paths):
		return ''
	if len(paths)==1:
		return paths[0]
	output=paths[0]
	for path in paths[1:]:
		output=_path_join(output,path)
	return output

class EmptyContext:
	def __enter__(self,*args):
		pass
	def __exit__(self,*args):
		pass

def median(values):
	values=sorted(values)
	length=len(values)
	assert length>0,'Cannot get median of empty list'
	if length%2:
		return  values[length//2]
	else:
		return (values[length//2]+values[length//2-1])/2

def mean(l):
	l=list(l)
	return sum(l)/len(l)

def std(l):
	u=mean(l)
	return mean((x-u)**2 for x in l)**.5

def blend(x,y,a):
	return a*y+(1-a)*x
	
def interp(x,*y):
	x=max(0,min(x,len(y)-1))
	if x==int(x):
		return y[int(x)]
	return blend(y[int(x)],y[int(x)+1],x-int(x))

def rjust(string:str,length:int,char:str=' ')->str:
	if len(string)<length:
		string=string+char*(length-len(string))
	return string

def ljust(string:str,length:int,char:str=' ')->str:
	if len(string)<length:
		string=char*(length-len(string))+string
	return string

def sign(number)->int:
	return 1 if number>0 else -1 if number<0 else 0

def note_to_pitch(note,*scale):
	#Usually scale will have length 12
	#Scale should be monotonically increasing
	return interp(note%(len(scale)-1),*scale)+scale[-1]*(note//(len(scale)-1))

def number_to_digits(number:int,num_digits:int)->list:
	#EXAMPLE:
	#     >>> base_ten(129,10)
	#    ans = [0, 0, 0, 0, 0, 0, 0, 1, 2, 9]
	assert isinstance(number,int),'base_ten only accepts integers'
	assert number>=0             ,'base_ten only accepts non-negative integers'
	return [number//(10**(num_digits-i-1))%10 for i in range(num_digits)]

def digits_to_number(digits:list):
	#EXAMPLE:
	#    >>> digits_to_number([1,2,3])
	#    ans = 123
	return sum(digit*10**i for i,digit in enumerate(reversed(digits)))

major_scale=[0,2,4,5,7,9,11,12]
natural_minor_scale=[0,2,3,5,7,8,10,12]
harmonic_minor_scale=[0,2,3,5,7,8,11,12]
blues_scale=[0,3,5,6,7,10,12]
chromatic_scale=[0,1,2,3,4,5,6,7,8,9,10,11,12]

def add_semitone_to_scale(scale:list,semitone:int)->None:
	assert 0 in scale and 12 in scale, 'All semitone-based scales must have 0 and 12 in them. Scale: %s'%str(scale)
	semitone=semitone%12
	if semitone in scale:
		return
	scale.append(semitone)
	scale.sort()

def remove_semitone_from_scale(scale:list,semitone:int)->None:
	assert 0 in scale and 12 in scale, 'All semitone-based scales must have 0 and 12 in them. Scale: %s'%str(scale)
	semitone=semitone%12
	if semitone==0:
		return
	scale[:]=[x for x in scale if x!=semitone]

class DraggableValue:
	def __init__(
			self,
			value=0,
			value_per_pos=1,
			min_value=None,
			max_value=None,
			min_pos=None,
			max_pos=None
			):
		#This class is for dragging values on the ribbons, for controlling CC midi valueues like a knob
		#min_pos, max_pos define the zone where a drag must start
		#min_value, max_value define the min and max value
		#value_per_pos determines how much value changes with pos
		self.value=value
		self.value_per_pos=value_per_pos
		self.min_value=min_value
		self.max_value=max_value
		self.min_pos=min_pos
		self.max_pos=max_pos
		self.release()

	def release(self):
		self.anchor_pos=None
		self.anchor_value=self.value
		return self.value

	def drag(self,pos):
		if self.anchor_pos is None:
			self.anchor_pos = pos
		if self.__contains__(self.anchor_pos):
			delta_pos = pos - self.anchor_pos
			self.value = self.anchor_value + self.value_per_pos * delta_pos
		if self.max_value is not None:self.value=min(self.max_value,self.value)
		if self.min_value is not None:self.value=max(self.min_value,self.value)
		return self.value

	@property
	def held(self):
		return self.anchor_pos is not None

	def __contains__(self,pos):
		#If a pos is in the drag-start zone
		if self.min_pos is not None and pos<self.min_pos: return False
		if self.max_pos is not None and pos>self.max_pos: return False
		return True

	@property
	def dragging(self):
		return self.held and self.anchor_pos in self

	def set_value(self,value):
		self.value=value

class NeopixelRegion:
	def __init__(self,start,end,color_on,color_off=None,on_select=None,data=None):
		#Colors are float colors
		#Start and end mark where the region is, measured in neopixels
		#Used for MIDI CC control, not for regular notes (it would be too slow right now - this implementation is not super efficient)
		self.start=start
		self.end  =end

		if color_off is None:
			r,g,b=color_on
			color_off=(r/6,g/6,b/6)

		self.color_on =float_color_to_byte_color(*color_on )
		self.color_off=float_color_to_byte_color(*color_off)

		self.on_select=on_select if on_select is not None else lambda:None

		self.data=data #Extra data to store here

	def __contains__(self,pos):
		return self.start<=pos<=self.end

	def draw(self,on=False):
		import lightboard.neopixels as neopixels
		#TODO: Can be optimized by directly saving the bytearray produced
		animate=True
		if not animate:
			r,g,b=self.color_on if on else self.color_off
		else:
			if not on:
				r,g,b=self.color_off
			else:
				#Interpolate between color on and off in a blinking fashion
				frequency=1
				alpha=(math.sin(seconds()*frequency*tau)+1)/2
				alpha=blend(alpha,1,.5)#Min alpha
				r,g,b = [floor(blend(x,y,alpha)) for x,y in zip(self.color_off,self.color_on)]
		start=self.start
		end  =self.end-1 #Don't overdraw with respect to when pos selects us
		neopixels.draw_line(start,end,r,g,b)

class SelectableNeopixelRegions:
	def __init__(self,regions=None):
		#Regions is a list of NeopixelRegion instances
		self.regions=regions if regions is not None else []
		self.selected=None
		self._prev_ribbon=None #When ribbon is changed, we also trigger on_select...

		assert isinstance(self.regions,list)
		assert all(isinstance(x,NeopixelRegion) for x in self.regions)

	def __contains__(self,pos):
		return any(pos in x for x in self.regions)

	def draw(self):
		for region in self.regions:
			if region is self.selected:
				region.draw(on=True)
			else:
				region.draw(on=False)

	def select(self,pos,ribbon=None):
		selected=None
		for region in self.regions:
			if pos in region:
				selected=region
		triggered=False
		if selected is not None and (selected!=self.selected or ribbon is not self._prev_ribbon):
			triggered=True
		self._prev_ribbon=ribbon
		self.selected=selected
		if triggered:
			selected.on_select()

	def __iadd__(self,region):
		#Add a region to regions
		self.regions.append(region)
		return self

	@property
	def data(self):
		if self.selected is not None:
			return self.selected.data
		else:
			return None