import board
import busio
from collections import OrderedDict
from urp import *
from linear_modules import *
import lightboard.buttons as buttons
import lightboard.neopixels as neopixels
from lightboard.config import config


calibration_weight_address='load_cell calibration weight'

uart =busio.UART(board.D29, board.D28, baudrate=115200, timeout=1000*(1/115200),receiver_buffer_size=2048) #Make timeout as small as possible without accidently not reading the whole line...

uart_stopwatch=Stopwatch()
REFRESH_INTERVAL=1/80 #How often should we poll the Nano? (It should output a message 80 times a second). Decreasing this means the weight sensors will be updated less frequently, but means other sensors will be updated faster
# REFRESH_INTERVAL=1 #How often should we poll the Nano? (It should output a message 80 times a second). Decreasing this means the weight sensors will be updated less frequently, but means other sensors will be updated faster

class LoadCellFilter:
	def __init__(self):
		self.soft_tether=SoftTether(10000)
		self.value=0
	def __call__(self,value):
		# value=self.soft_tether(value)
		self.value=value
		return value

class LoadCellCalibration:
	def __init__(self,load_cell):
		self.load_cell=load_cell
		self.raw_tare_value_address     ='load_cell calibration %s raw_tare_value'     %self.load_cell.name
		self.grams_per_raw_value_address='load_cell calibration %s grams_per_raw_value'%self.load_cell.name

		self.load()

	def load(self):
		#Load calibration from config
		#The following two values should be calibrated during runtime; they shouldn't actually be 0 and 1 (0 and 1 are just placeholder values here)
		self.raw_tare_value     =config[self.raw_tare_value_address     ] if self.raw_tare_value_address      in config else 0
		self.grams_per_raw_value=config[self.grams_per_raw_value_address] if self.grams_per_raw_value_address in config else 1

	def save(self):
		config[self.raw_tare_value_address     ] = self.raw_tare_value
		config[self.grams_per_raw_value_address] = self.grams_per_raw_value

	def get_precise_raw_reading(self,message:str):
		import lightboard.display as display
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
		import lightboard.widgets as widgets
		import lightboard.display as display

		#grams represents the weight of the object that we use to calibrate the load cell
		with display.TemporarySetText('Please take all weight off \nload cell '+repr(self.load_cell.name)+'\nThen press green button 1'):
			with buttons.TemporaryMetalButtonLights(1,0,0):
				with buttons.TemporaryGreenButtonLights(1,0,0,0):
					while not buttons.green_1_press_viewer.value:
						if buttons.metal_press_viewer.value and widgets.input_yes_no("Cancel calibration?"):
							return
					buttons.green_button_1.light=False

					self.raw_tare_value=self.get_precise_raw_reading('Please don\'t wobble the lightwave!\nPreparing to calibrate (taring...)\n'+repr(self.load_cell.name))
					display.set_text('Taring complete! Please put your\n'+str(grams)+' gram weight on load cell\n'+repr(self.load_cell.name)+'\nThen press the green button')

					buttons.green_button_1.light=True
					while not buttons.green_1_press_viewer.value:
						if buttons.metal_press_viewer.value and widgets.input_yes_no("Cancel calibration?"):
							return

					buttons.green_button_1.light=False

					raw_weighed_value=self.get_precise_raw_reading('Please don\'t wobble the lightwave!\nPreparing to calibrate...\n(Using '+str(grams)+' grams)\n'+repr(self.load_cell.name))
					display.set_text('Weighing complete!')

					self.grams_per_raw_value=grams/(raw_weighed_value-self.raw_tare_value)
					display.set_text('Weighing complete!')
					self.run_test()

					if widgets.input_yes_no('Save this calibration?\nLoad Cell: '+self.load_cell.name):
						self.save()

	def run_test(self):
		import lightboard.display as display
		movmean=MovingAverage(10)
		buttons.green_button_1.light=True
		while not buttons.green_1_press_viewer.value:
			value=self.value
			value=movmean(value)
			display.set_text('Testing load cell:\n%s\n\n%15.3f\n\nPress green button 1 to continue'%(self.load_cell.name,value))
		buttons.green_button_1.light=False

	@property
	def value(self):
		#TODO: this object shouldn't be responsible for applying the filter
		return self(self.load_cell.filter(self.load_cell.value))

	def __call__(self,raw_value):
		return (raw_value-self.raw_tare_value)*self.grams_per_raw_value

def test_all_load_cells(raw=False):
	import lightboard.display as display
	#Run a test where we show all load cells' weights at once. TODO: Later on create a graph for this.
	movmeans=[MovingAverage(1) for _ in load_cells]
	buttons.green_button_1.light=True
	while not buttons.green_1_press_viewer.value:
		values=[movmean(load_cell.calibration.value if not raw else load_cell.raw_value) for movmean,load_cell in zip(movmeans,load_cells)]
		text='\n'.join([rjust(load_cell.name,20)+'%10.2f'%value for load_cell,value in zip(load_cells,values)])
		text+='\n\nSum: %15.2f'%sum(values)
		display.set_text('Testing all load cells:\n\n'+text+'\n\nPress green button 1 to continue')
	buttons.green_button_1.light=False

def tare_all_load_cells():
	import lightboard.display as display
	import lightboard.buttons as buttons
	import lightboard.widgets as widgets
	#TODO: Unredundify code from get_precise_raw_reading
	num_samples=1000
	totals=[0]*len(load_cells)
	if not widgets.input_yes_no('Are you ready to tare?\nRemove all objects from the lightboard'):
		return
	
	display.set_text('Please wait a few seconds...')
	for _ in range(num_samples):
		for i,load_cell in enumerate(load_cells):
			totals[i]+=load_cell.raw_value
		sleep(REFRESH_INTERVAL)

	means=[total/num_samples for total in totals]

	for mean,load_cell in zip(means,load_cells):
		load_cell.calibration.raw_tare_value=mean

	test_all_load_cells()

	if widgets.input_yes_no('Keep this calibration?'):
		for load_cell in load_cells:
			load_cell.calibration.save()
		display.set_text("Saved!")
		sleep(.25)

class LoadCell:
	def __init__(self,name:str):
		self.name=name
		self.filter=LoadCellFilter()
		self.calibration=LoadCellCalibration(self)
		self._raw_value=0

	@property
	def raw_value(self):
		refresh()
		return self._raw_value
	
	@raw_value.setter
	def raw_value(self,value):
		self._raw_value=value
		self.filter(value)

	@property
	def value(self):
		refresh()
		return self.filter.value

	def __repr__(self):
		return self.name

#These names maybe shouldn't have spcaes in them, because they're going to be in the config. It probably doesn't matter tho - it's just a weird structure for the config json.
top_left =LoadCell('1:Top-Left'    )
top_right=LoadCell('2:Top-Right'   )
mid_left =LoadCell('3:Middle-Left' )
mid_right=LoadCell('4:Middle-Right')
bot_left =LoadCell('5:Bottom-Left' )
bot_right=LoadCell('6:Bottom-Right')

load_cells=[top_left,top_right,
            mid_left,mid_right,
            bot_left,bot_right]

SILENT_ERRORS=False

def error_blink():
	colors=[(0,0,1),(0,1,0),(1,0,0)]
	if buttons.metal_button.color not in colors:
		buttons.metal_button.color=(0,0,1)
	else:
		color=buttons.metal_button.color
		color=colors[(colors.index(color)+1)%len(colors)]
		buttons.metal_button.color=color

last_message=None
raw_weights=[0]*6
raw_imu    =[0]*6
def refresh():
	#TODO: We need an explanation for why using readline twice seems to make everything ok. Maybe we don't need to make a complex stateful parser?
	if uart_stopwatch.toc()<REFRESH_INTERVAL:
		return
	global last_message,raw_weights,raw_imu
	# tic()
	# uart.write_timeout(0)

	# tic()
	uart.reset_input_buffer()
	uart.write(b'X') #Write exactly 1 byte to the nano (doesnt matter what that byte is)
	data=uart.readline()
	# ptoc() #This takes almost exactly 1/100 seconds: .009s

	# ptoc()
	if data:
		uart_stopwatch.tic()
		try:
			last_message=data.decode().strip()
			#Should look like:
			#	last_message=">,-178070,-251194,-64062,185960,50025,-168551,0.6081,-0.5267,8.9232,0.0580,0.0112,0.0548,<"
			assert last_message.count(',')==6*2-1+2,'Failed Commacount: '+repr(last_message)#'There should be 12 comma-separated values', otherwise we likely misread the NANO's message
			assert last_message[0]=='>' and last_message[-1]=='<','Failed ><: '+repr(last_message)
		except Exception as e:
			if not SILENT_ERRORS:
				import lightboard.display as display
				print("Nano UART Error:",str(e))
				error_blink()
				display.set_text('+++NANO UART ERROR+++\n\n\n'+str(len(data))+'\n'+str(e))
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
			except Exception as e:
				if not SILENT_ERRORS:
					import lightboard.display as display
					print_error("Nano Parsing Error:",str(e))
					display.set_text(str(len(data))+'\nParse\n'+str(e))
					error_blink()
				return
	else:
		if not SILENT_ERRORS:
			# If you're getting this a lot, it probably means uart.readline() timed out...
			# Pro tip: This often means that the nano isn't getting enough power. For example, when all the neopixels are on full brightness.
			import lightboard.display as display
			error_blink()
			display.set_text("NANO SENT NO DATA (EMPTY LINE)\nIs the nano getting enough power?")

def get_calibration_weight():
	if calibration_weight_address not in config:
		config[calibration_weight_address]=250
	return config[calibration_weight_address]

def input_set_calibration_weight():
	import lightboard.widgets as widgets
	try:
		config[calibration_weight_address]=widgets.input_integer(get_calibration_weight(),prompt='Enter calibration weight:')
	except KeyboardInterrupt:
		pass

def get_imu():
	refresh()
	return raw_imu[:3],raw_imu[3:]

def get_total_load_cell_weight():
	#TODO: Add calibration for the total weight, and accelerometer correction
	return sum(load_cell.calibration.value for load_cell in load_cells)

def test_total_load_cell_weight():
	import lightboard.display as display
	movmean=MovingAverage(1)
	buttons.green_button_1.light=True
	while not buttons.green_1_press_viewer.value:
		value=get_total_load_cell_weight()
		value=movmean(value)
		display.set_text('Testing raw calibrated\nload cell total:\n\n%15.3f\n\nPress green button 1 to continue'%(value))
	buttons.green_button_1.light=False

def test_uart_load_cells():
	#Use this to debug the Nano's raw outputs in an Arduino serial graph
	while True:
		uart.reset_input_buffer()
		uart.write(b'X') #Write exactly 1 byte to the nano (doesnt matter what that byte is)
		data=uart.readline()
		print(data.decode()[2:-3])

def test_pressure():
	import lightboard.display as display
	movmean=MovingAverage(1)
	buttons.green_button_1.light=True
	while not buttons.green_1_press_viewer.value:
		# refresh()
		timer=Stopwatch()
		value=get_pressure()
		# value=movmean(value)
		# display.set_text('Testing pressure:\n\n%15.3f\n\nPress green button 1 to continue'%(value))
		neopixels.display_line(0,min(neopixels.length,max(0,value*neopixels.length)))
		display.set_text('Pressure:\n%1.4f\nTime: %1.4f\n\nPress metal to exit'%(value,timer.toc()))

	buttons.green_button_1.light=False

def test_imu():
	import lightboard.display as display
	movmean=MovingAverage(1)
	buttons.green_button_1.light=True
	while not buttons.green_1_press_viewer.value:
		# refresh()
		timer=Stopwatch()
		value=sum(get_imu()[1])*.1+.5
		value=sum(x**2 for x in get_imu()[1])*.1+.5#Rotational accel
		value=get_imu()[0][2]/10#gravity
		# value=sum(get_imu()[0])*.1+.5
		# value=movmean(value)
		# display.set_text('Testing pressure:\n\n%15.3f\n\nPress green button 1 to continue'%(value))
		neopixels.display_line(0,min(neopixels.length,max(0,value*neopixels.length)))
		display.set_text('IMU:\n%1.4f\nTime: %1.4f\n\nPress metal to exit'%(value,timer.toc()))

	buttons.green_button_1.light=False


weight_per_pressure_address='load_cell weight_per_pressure'

def get_weight_per_pressure():
	return config[weight_per_pressure_address] if weight_per_pressure_address in config else 1000

def set_weight_per_pressure(value):
	config[weight_per_pressure_address]=value

def input_set_weight_per_pressure():
	import lightboard.widgets as widgets
	config[weight_per_pressure_address]=widgets.input_integer(get_weight_per_pressure(),prompt='How many grams per pressure?')

def get_pressure():
	#1 is for full pressure, 0 is for no pressure. This is turned into MIDI. 
	#This is not weight in grams, or number of neopixels. It's a scale from 0 to 1.
	return get_total_load_cell_weight()/get_weight_per_pressure()

def show_calibration_menu():
	import lightboard.widgets as widgets

	def calibrate_load_cells(testing=False):
		try:
			while True:
				load_cell=widgets.input_select(load_cells,prompt='Calibration:\nSelect a load cell',
				                               can_cancel=True,must_confirm=False,confirm_cancel=False)
				if task==calibrate_cell:
					load_cell.calibration.run_calibration(get_calibration_weight())
				else:
					assert task==test_cell
					load_cell.calibration.run_test()
		except KeyboardInterrupt:
			pass

	options = OrderedDict()

	options['Test Load Cell'          ] = lambda: calibrate_load_cells(testing=True)
	options['Test All Load Cells'     ] = lambda: test_all_load_cells(raw=False)
	options['Test All Load Cells Raw' ] = lambda: test_all_load_cells(raw=True)
	options['Calibrate Load Cell'     ] = lambda: calibrate_load_cells(testing=False)
	options['Set Calibration Weight'  ] = input_set_calibration_weight
	options['Tare All Load Cells'     ] = tare_all_load_cells
	options['Test Raw Total Weight'   ] = test_total_load_cell_weight
	options['Test Pressure'           ] = test_pressure
	options['Test IMU'                ] = test_imu
	options['Set Pressure Coefficient'] = input_set_weight_per_pressure

	widgets.run_select_subroutine(options)