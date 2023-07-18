from urp import *

class HistogramFitter:
	#This code is really messy. It's ok though...
	#Memory improvements might be made by using lists or arrays instead of dicts...
	def __init__(self,bin_size=None,file_path=None,auto_load=True):
		self.file_path=file_path
		assert self.file_path is None or isinstance(self.file_path,str)
		if auto_load and self.file_path is not None and path_exists(self.file_path):
			try:
				self.load_from_file(self.file_path)
			except Exception:
				print("Failed to auto_load HistogramFitter file: "+self.file_path)
				raise
		else:
			assert bin_size is not None,'HistogramFitter: Did not load from file, but bin_size was None - we have nothing to initialize with.'
			self.bin_size=bin_size
			self.histogram_sums={}
			self.histogram_freqs={}
			self._verified=False

	def save_to_file(self,path=None):
		if path is None:
			path=self.file_path
		self.verify()
		data = self._verified, self.bin_size, self.histogram_sums, self.histogram_freqs, self.max_bin, self.min_bin
		object_to_file(data,path)

	def load_from_file(self,path):
		if path is None:
			path=self.file_path
		data=file_to_object(path)
		self._verified, self.bin_size, self.histogram_sums, self.histogram_freqs, self.max_bin, self.min_bin = data
		assert self._verified,'Internal logical assertion: self._verified should be True because self.verify() is called before self.save_to_file() completes'
		
	def add_sample(self,x,y):
		x/=self.bin_size
		x=int(x)
		if x not in self.histogram_sums:
			self.histogram_sums[x]=0
		if x not in self.histogram_freqs:
			self.histogram_freqs[x]=0
		self.histogram_freqs[x]+=1
		self.histogram_sums[x]+=y
		self._verified=False
		
	def __getitem__(self,x):
		self.verify()
		if   x>self.max_bin: x=self.max_bin
		elif x<self.min_bin: x=self.min_bin
		return self.histogram_sums[x]/self.histogram_freqs[x]
	
	def verify(self):
		if self._verified:
			#Don't waste time
			return
		#Internal assertion
		assert set(self.histogram_sums)==set(self.histogram_freqs)
		
		#Fill in any holes in the histogram
		min_bin=min(self.histogram_sums)
		max_bin=max(self.histogram_sums)
		self.max_bin=max_bin
		self.min_bin=min_bin
		prev_freq=self.histogram_freqs[min_bin]
		prev_sum =self.histogram_sums [min_bin]

		means=[None]*(max_bin-min_bin+1)
		for key in self.histogram_freqs:
			if self.histogram_freqs[key]>0:
				means[key-min_bin]=self.histogram_sums[key]/self.histogram_freqs[key]
		def tween(a,b,n):
			# >>> tween(0,6,3)
			#ans = [0.0, 3.0, 6.0]
			# >>> tween(0,6,4)
			#ans = [0.0, 2.0, 4.0, 6.0]
			delta=(b-a)/(n-1)
			return [a+i*delta for i in range(n)]
		
		def none_indices(array):
			#First and last index of the first contiguous clump of None's in an array
			assert None in array
			first=array.index(None)
			last=first
			while array[last+1] is None:
				last+=1
			return first,last
			
		def none_fill(array):
			# >>> none_fill([1,2,None,None,5,6])
			#ans = [1, 2, 3.0, 4.0, 5, 6]
			# >>> none_fill([1,2,None,None,5,6,None,None,None,None,11])
			#ans = [1, 2, 3.0, 4.0, 5, 6, 7.0, 8.0, 9.0, 10.0, 11]
			while None in array:
				first,last=none_indices(array)
				array[first:last+1]=tween(array[first-1],array[last+1],last-first+3)[1:-1]
			return array

		means=none_fill(means)
		for i in range(len(means)):
			key=i+min_bin
			if key not in self.histogram_freqs or self.histogram_freqs[key]==0:
				self.histogram_freqs[key]=1
				self.histogram_sums[key]=means[i]

		for i in range(min_bin,max_bin+1):
			#Todo: Add linear interpolation instead of the simple step function used here
			if i not in self.histogram_sums:
				self.histogram_sums[i]=prev_sum
				assert i not in self.histogram_freqs
				self.histogram_freqs[i]=prev_freq
				
			prev_freq=self.histogram_freqs[i]
			prev_sum =self.histogram_sums [i]
			
		self._verified=True

	@property
	def is_fitted(self):
		#If this HistogramFitter is virgin, return False
		#If there's even one calibration point though, return True
		return len(self.histogram_sums)>0

	def __call__(self,x):
		if not self.is_fitted:
			#If we haven't calibrated anything yet, just return the identity...
			#...it makes more sense than crashing does in most contexts.
			return x

		x/=self.bin_size
		x-=1/2 #Correct the placement of the bins
		if x==int(x):
			return self[int(x)]
		alpha=x-int(x)
		out = self[int(x)]+alpha*(self[int(x)+1]-self[int(x)])
		out += 1/2 #SHIFT HACK - this should be a config parameter
		return out

class NeopixelRibbonVoltageCalibrator:
	def __init__(self,reader,gate):
		#This object is meant to fit a raw analog input to the voltage drops caused by neopixels
		#As it turns out, from many experiments, the voltage drop proportion is a function to the sum of all the color values in the neopixel strip
		#    (This assumption might not hold for other neopixel strips; but with this one, red green and blue all have the same effect on the ribbon's voltage drop)
		#    (Also, the analog input drop on the ribbon is proportional to the value of the ribbon when all lights are off, assuming the user is pressing on it)
		#TODO: Create a way to save and load calibrations
		self.fit=HistogramFitter(50)
		assert callable(reader),'reader is supposed to be a function that returns a numerical value'
		assert callable(gate),'gate is supposed to be a function that returns a boolean value indicating if the ribbon is being pressed'
		self.reader=reader
		self.gate=gate

	def calibrate(self,num_samples=2000):
		#When this is calibrating, please move your finger along the ribbon...
		#Keep doing that until the lights stop flashing...

		while not self.gate():
			pass

		for _ in range(num_samples):

			random_partitions=random_partition(numpix*3,3)
			random_colors=bytearray([  0]*random_partitions[0]
								   +[127]*random_partitions[1]
								   +[255]*random_partitions[2])
			shuffle(random_colors)

			progress_pixel=int(numpix*(_/num_samples))
			random_colors[progress_pixel*3+0]=0
			random_colors[progress_pixel*3+1]=0
			random_colors[progress_pixel*3+2]=0

			write_to_neopixels(pixel_off)
			originalval=self.reader()
			write_to_neopixels(random_colors)
			newval=self.reader()

			factor=originalval/newval

			x=sum(random_colors)
			x=ads_a_single.value
			y=math.log(factor)

			#Print out the results so we can plot them in desmos
			print('%i , %.9f'%(x,y))

			self.fit.add_sample(x,y)

	def __call__(self):
		return self.reader()*math.exp(self.fit(sum(neopixel_data)))

class AddressedConfig:
	def __init__(self,file_path,auto_save=True):
		self.auto_save=auto_save
		self.file_path=file_path
		# self.cursor=AddressCursor(self) #This works in CPython...Idk why it doesn't work in circuitpython...
		if path_exists(self.file_path):
			self.load()
		else:
			self._data={}
			self.save()
			
	def save(self):
		object_to_file(self.data,self.file_path)
	def load(self):
		self._data=file_to_object(self.file_path)
	def clear(self):
		self.data={}

	def get_with_default(self,address,default=None):
		if address not in self and default is not None:
			self[address]=default
		return self[address]

	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self,value):
		self._data=value
		if self.auto_save:
			self.save()
		
	@staticmethod
	def _as_address(address):
		#The following four expressions should return the same result:
		#    self['hello']
		#    self['hello',]
		#    self[['hello']]
		#    self[('hello',)]
		#Also, the following expressions should return the same result:
		#    self['hello world wow']
		#    self['hello','world','wow']
		#    self['hello world','wow']
		#    self['hello    world','wow']
		#    self['hello','world wow']
		if isinstance(address,list):
			address=tuple(address)
		elif not isinstance(address,tuple):
			address=(address,)
		address=tuple(map(str,address))
		address=sum((tuple(key.split()) for key in address),tuple())
		return address
		
	def __getitem__(self,address):
		address=self._as_address(address)
		
		output=self.data
		for key in address:
			assert key in output,'Invalid address at %s: %s'%(key,'.'.join(address))#Don't just fail; tell us where on the address it failed.
			output=output[key]
		
		return output

	def __setitem__(self,address,value):
		address=self._as_address(address)
		if len(address)==0:
			#This is an edge case
			self.data=value
			return  
		if len(address)>1:
			self.burrow(address)
		self[address[:-1]][address[-1]]=value
		if self.auto_save:
			self.save()
	
	def __contains__(self,address):
		address=self._as_address(address)
		cursor=self.data
		for key in address:
			if key not in cursor:
				return False
			cursor=cursor[key]
		return True
	
	def burrow(self,address,bulldoze=False):
		#Attempt to make the entire folder structure for a given address
		#If not bulldoze, it's not allowed to overwrite anything
		address=self._as_address(address)
		
		history=tuple()
		cursor=self
		for key in address:
			history+=(key,)
			if key not in cursor:
				cursor[key]={}
				cursor=cursor[key]
			elif isinstance(cursor[key],dict):
				cursor=cursor[key]
			else:
				return #Don't throw an error...just stop here. It's ok.
				# assert bulldoze,'Cant burrow %s without bulldozing: address %s is a %s'%('.'.join(address),'.'.join(history),str(type(cursor[key])))
	
	def __repr__(self):
		return repr(self.data)
	
class AddressCursor:
	#I don't know why this doesn't work in circuitpython...this works in CPython.
	#Apparently the CircuitPython object class doesn't implement __setattr__??
	#Normally we can do cursor.hello={} then cursor.hello.world="!" and then repr(root)=={'hello': {'world': '!'}}
	def __init__(self,root:AddressedConfig,address=tuple()):
		object.__setattr__(self,'root',root)
		object.__setattr__(self,'address',address)
	def __setattr__(self,key,value):
		address=object.__getattribute__(self,'address')
		address+=(key,)
		object.__getattribute__(self,'root')[address]=value
	def __getattribute__(self,key):
		address=object.__getattribute__(self,'address')
		address+=(key,)
		root=object.__getattribute__(self,'root')
		if address not in root:
			raise KeyError('Invalid address: '+'.'.join(address))
		if isinstance(root[address],dict):
			return type(self)(root,address)
		else:
			return root[address]