from urp import *

class LinearModule:
	#Subclasses should implement the following three methods:
	# def __init__(self,*args,**kwargs):
	# 	pass
	# def __call__(self,value):
	# 	pass
	# def clear(self):
	# 	pass
	#Note that none of the LinearModule classes in this python module are actually subclasses of LinearModule, as that would make the code slower.
	pass

class Identity:
	def __init__(self):
		pass
	def __call__(self,value):
		return value
	def clear(self):
		pass

class Squelcher:#(LinearModule):
	def __init__(self,callable,value=None,error=None,exception_class=Exception):
		#Interfaces like a linear module but can be used with more than just numerical values...
		self.callable=callable
		self.error=error
		self.value=value
		self.exception_class=exception_class
	def __call__(self):
		self.error=None
		try:
			self.value=self.callable()
		except self.exception_class as error:
			self.error=error
		return self.value
	def clear(self):
		self.value=self.error=None

#These LinearModule-like classes are all callable when inputting a new value, and all store a 'value' parameter to get the last calulated value 
#It's supposed to be pythonic; as opposed to jWave (which implicitly creates a tree). This is more like pytorch than tensorflow...let's see how it goes. 
class Tether:#(LinearModule):
	def __init__(self,size=1,value=None):
		self.size=size
		self.value=value
	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			self.value=clamp(self.value,value-self.size,value+self.size)
		return self.value
	def clear(self):
		self.value=None

class SoftTether:#(LinearModule):
	#Acts similar to Tether, but has nicer properties (is smoother, and large jumps cause near-perfect centering for example)
	def __init__(self,size=1,value=None):
		self.size=size
		self.value=value
	def __call__(self,value):
		if self.value is None or self.size==0:
			self.value=value
		else:
			alpha=1-2.718**(-((value-self.value)/self.size)**2)
			self.value=alpha*value+(1-alpha)*self.value
		return self.value
	def clear(self):
		self.value=None

class Legato:#(LinearModule):
	def __init__(self,alpha,value=None):
		self.value=value
		self.alpha=alpha
	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			self.value=self.alpha*value+self.value*(1-self.alpha)
		return self.value
	def clear(self):
		self.value=None

class Differential:#(LinearModule):
	#TODO: Make a version of this class that takes time into account?
	def __init__(self,prev=None,value=None):
		self.prev=prev
		self.value=value
	def __call__(self,value):
		if self.value is None:
			self.prev=value
		self.value=value-self.prev
		self.prev=value
		return self.value
	def clear(self):
		self.prev=self.value=None

class MovingAverage:#(LinearModule):
	def __init__(self,length:int):
		#A moving average with 'length' number of samples
		#Todo: To save memory, make a general-purpose sliding window class so that MovingAverage's window can be shared with Delay's window can be shared with MovingMedian's window
		#Todo: Dynamically adjustable length
		assert length>0,'Must have a positive length'
		self.values=[0]*length
		self._length=length
		self._total=0
		self._count=0
		self._cursor=0
	def __call__(self,value):
		self._count=min(self._length,self._count+1)
		self._cursor%=self._length
		self._total-=self.values[self._cursor]
		self.values[self._cursor]=value
		self._total+=value
		self._cursor+=1
		self.value=self._total/self._count
		return self.value
	@property
	def length(self):
		return len(self.values)
	def clear(self):
		self._total=0
		self._count=0
		self._cursor=0
		self.values=[0]*self.length

class MovingMedian:#(LinearModule):
	#TODO: Make this more efficient; perhaps use ulab?
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.values=self.values[-self.length:]
		self.value=median(self.values)
		return self.value
	def clear(self):
		self.values.clear()

class MovingMedianBasedDelay:#(LinearModule):
	#TODO: Make this more efficient; perhaps use ulab?
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.values=self.values[-self.length:]
		length=len(self.values)
		if length%2:
			self.value=self.values[length//2]
		else:
			self.value=(self.values[length//2]+self.values[length//2-1])/2
		return self.value
	def clear(self):
		self.values.clear()

class ReluctantDrop:
	#Can be turned on quickly, but has to be consistently off for a certain period of time to be turned off
	def __init__(self,time,value=False):
		#Given time in seconds
		self.value=value
		self.time=0
		self._prev_timestamp=None
	def __call__(self,value:bool):
		if value:
			self._prev_timestamp=seconds()
		if self.value and not value and seconds()-self._prev_timestamp>self.time:
			self.value=False
		else:
			self.value=value

class Delay:
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.value=self.values[0]
		self.values=self.values[-self.length:]
		return self.value
	def clear(self):
		self.values.clear()

class MovingMinimum:
	#TODO: Make this more efficient; perhaps use a heap?
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.values=self.values[-self.length:]
		self.value=min(self.values)
		return self.value
	def clear(self):
		self.values.clear()

class MovingMaximum:
	#TODO: Make this more efficient; perhaps use a heap?
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self.values=[]
	def __call__(self,value):
		self.values.append(value)
		self.values=self.values[-self.length:]
		self.value=max(self.values)
		return self.value
	def clear(self):
		self.values.clear()

class MovingRange:
	#TODO: Make this more efficient; perhaps use only one list (not two idential lists stored separately in MovingMaximmum and MovingMinimum)
	def __init__(self,length):
		assert length>0,'Must have a positive length'
		self.length=length
		self._moving_maximum=MovingMaximum(length)
		self._moving_minimum=MovingMinimum(length)
	def __call__(self,value):
		lower=self._moving_minimum(value)
		upper=self._moving_maximum(value)
		assert upper>=lower,'Internal logical assertion: Cannot have negative range'
		self.value=upper-lower
		return self.value
	def clear(self):
		self._moving_minimum.clear()
		self._moving_maximum.clear()

class AntiJump:
	def __init__(self,threshold,length=2,value=None):
		#Require the inputs to make only small jumps (where the range across the length is less than the threshold), or else it won't update
		#A good alternative to a median; it means less latency
		assert length>0,'Must have a positive length'
		assert threshold>=0,'Must have a non-negative jump threshold'
		self.length=length
		self.value=value
		self.threshold=threshold
		self._moving_range=MovingRange(length)

	def __call__(self,value):
		if self.value is None:
			self.value=value
		else:
			range=self._moving_range(value)
			assert range>=0,'Internal logical assertion of MovingRange'
			if range<self.threshold:
				self.value=value
		return self.value

	def clear(self):
		self.value=None
		self._moving_range.clear()

class MedianBasedVibrato:
	#Extracts only the vibrato component
	def __init__(self,length):
		if not length%2:
			length+=1 #Length should be odd
		self.delay=Delay(length)
		self.delay=MovingMedianBasedDelay(length*2+1)
		self.moving_median=MovingMedian(length*2+1)
		self.length=length
		self.wait=False
	def __call__(self,value):
		d=self.delay(value)
		m=self.moving_median(value)
		if len(self.delay.values)<self.length:
			self.value=0
			return self.value
		print(m*100,d*100,m-d*100)
		self.value=m-d
		# self.value=self.delay(value)-self.moving_median(value)
		return self.value
	def clear(self):
		self.delay.clear()
		self.moving_median.clear()





