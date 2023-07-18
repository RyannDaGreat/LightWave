import lightboard.buttons as buttons
from lightboard.config import config
from urp import *
from collections import OrderedDict

def input_yes_no(prompt):
	import lightboard.display as display
	with buttons.TemporaryGreenButtonLights(1,0,0,0), buttons.TemporaryMetalButtonLights(1,0,0):
		# with display.TemporarySetText(prompt+'\n(Button 1 -> Yes, Metal Button -> No)'):
			display.set_text(prompt+'\nButton 1 -> Yes, Metal Button -> No')
			while True:
				green_val = buttons.green_1_press_viewer.value
				metal_val = buttons.metal_press_viewer.value
				if metal_val:
					return False
				if green_val:
					return True
				buttons.sleep_debounce() #Without this, pressing the metal button might register twice. I think it's because the metal button has worse debounce than the green buttons.

def input_select(options,prompt='Please select an option:',can_cancel=False,must_confirm=True,num_options_per_page=13,confirm_cancel=True):
	import lightboard.buttons as buttons
	import lightboard.display as display

	prompt_lines=prompt.split('\n')
	prefix=prompt_lines+['Green: 3,1 -> Up/Down, 2 -> Select']
	if can_cancel:
		prefix+=['Metal: Cancel']
	
	colors=[0x88FF88]*len(prompt_lines)+[0x448888]*2

	page_num=0
	num_pages=len(options)//num_options_per_page
	prefix_page_num_index=0
	def update_prefix_page_num():
		prefix[prefix_page_num_index]='Showing page %i of %i'%(page_num+1,num_pages+1)
	if num_pages>0:
		colors+=[0xBB8844]
		prefix_page_num_index=len(prefix)
		prefix+=[None]#Will be updated by update_prefix_page_num
		update_prefix_page_num()
	options_offset=0

	prefix+=['']

	index=0
	with buttons.TemporaryGreenButtonLights(1,1,1,0):
		with buttons.TemporaryMetalButtonLights(1,0,1) if can_cancel else buttons.TemporaryMetalButtonLights(0,0,0):
			while True:
				if buttons.green_1_press_viewer.value:
					index+=1
				if buttons.green_3_press_viewer.value:
					index-=1
				if buttons.green_2_press_viewer.value:
					if not must_confirm or input_yes_no("Are you sure you want to select\n    "+repr(options[index])):
						return options[index]
				if buttons.metal_press_viewer.value and can_cancel and (not confirm_cancel or input_yes_no("Are you sure you want to cancel?")):
					raise KeyboardInterrupt

				index%=len(options)
				page_num=index//num_options_per_page
				options_offset=page_num*num_options_per_page
				visible_options=options[options_offset:options_offset+num_options_per_page]

				update_prefix_page_num()
				display.set_menu(labels=prefix+visible_options,
				                 index =len(prefix)+index%num_options_per_page,
				                 colors=colors)

def run_select_subroutine(options:OrderedDict,prompt='What do you want to do?',loop=True):
	#Lets you select a subroutine, then runs it
	#Options is an OrderedDict mapping strings to zero-argument callables

	import lightboard.buttons as buttons
	import lightboard.display as display

	while True:
		try:
			selected_key=input_select(list(options),prompt=prompt,can_cancel=True,must_confirm=False,confirm_cancel=False)
			subroutine=options[selected_key]
			subroutine()
			if not loop:
				break
		except KeyboardInterrupt:
			break

def edit_config_int(address,*,min_value=None,max_value=None,default=0,message=None,on_update=None,exponential=True):
	import lightboard.display as display
	
	#TODO: Create input_int and use that in edit_config_int (refactoring)
	if address not in config:
		config[address]=default
	
	original_value=config[address]
	value=original_value

	old_config_auto_save=config.auto_save
	config.auto_save=False

	try:
		with buttons.TemporaryGreenButtonLights(1,1,1,0), buttons.TemporaryMetalButtonLights(1,0,1):
			def update_display():

				if min_value is not None and max_value is not None:
					bounds_string='Int between %i and %i'%(min_value,max_value)
				elif min_value is None and max_value is not None:
					bounds_string='Int at most %i'%max_value
				elif max_value is None and min_value is not None:
					bounds_string='Int at least %i'%min_value
				elif max_value is None and min_value is None:
					bounds_string=''

				message_lines=str(message).splitlines() if message is not None else []

				display.set_menu(labels=message_lines+['Editing '+address,
				                         bounds_string,
				                         '    Green 3 -> +%i'%delta,
				                         '    Green 2 -> Done',
				                         '    Green 1 -> -%i'%delta,
				                         '    Metal -> Cancel',
				                         '',
				                         address+' = '+str(value),
				                         ],
				                 colors=[0xFFFF88]*len(message_lines)+[0xFFFFFF,
				                         0xFFFFFF,
				                         0x00FF00,
				                         0x00FF00,
				                         0x00FF00,
				                         0xFF00FF,
				                         ]
				                )
			while True:
				buttons.green_button_1.light=value!=min_value
				buttons.green_button_1.light=value!=max_value
				
				if exponential:
					delta=10**(len(str(value))-1)
				else:
					delta=1

				if buttons.green_1_press_viewer.value:
					value-=delta
					if min_value is not None:
						value=max(min_value,value)

				if buttons.green_3_press_viewer.value:
					value+=delta
					if max_value is not None:
						value=min(max_value,value)

				if buttons.green_2_press_viewer.value:
					if input_yes_no("Are you sure you want to change\n'%s' from \n(old) %i to %i (new)?"%(address,original_value,config[address])):
						config[address]=value
						config.save()
						display.set_text('Confirmed: set %s to %i'%(address,config[address]))
						from time import sleep
						sleep(.5)
						return

				if buttons.metal_press_viewer.value:
					if input_yes_no("Are you sure you want to cancel\n and keep %s as %i?"%(address,original_value)):
						config[address]=original_value
						return

				if on_update is not None and config[address]!=value:
					config[address]=value
					try:
						on_update()
					finally:
						config[address]=original_value
						
				update_display()
	finally:
		config.auto_save=old_config_auto_save

def input_integer(initial_value:int=0,num_digits:int=6,allow_negative:bool=False,must_confirm:bool=True,prompt='Please input an integer'):
	import lightboard.buttons as buttons
	import lightboard.display as display

	assert not allow_negative,'allow_negative is not supported yet'
	assert     must_confirm  ,'not must_confirm is not supported yet'

	digits=number_to_digits(abs(initial_value),num_digits)[::-1]

	prefix =prompt.split('\n')
	prefix+=['']
	prefix+=['Green: 1,2 -> Dec/Inc','Green: 3,4 -> Down/Up']
	prefix+=['Metal: Confirm','']
	prefix+=['']

	def current_value():
		return digits_to_number(digits[::-1])

	index=0

	with buttons.TemporaryGreenButtonLights(1,1,1,1):
		with buttons.TemporaryMetalButtonLights(0,1,1):
			while True:
				if buttons.green_1_press_viewer.value:
					digits[index]-=1
					digits[index]%=10
				if buttons.green_2_press_viewer.value:
					digits[index]+=1
					digits[index]%=10
				if buttons.green_3_press_viewer.value:
					index+=1
					index%=len(digits)
				if buttons.green_4_press_viewer.value:
					index-=1
					index%=len(digits)
				if buttons.metal_press_viewer.value:
					return current_value()

				body=[str(digit)+'0'*i for i,digit in enumerate(digits)]
				suffix=['','Value: %i'%current_value()]
				colors=[0x88FF88]*len(prefix)+[0xFFFFFF]*len(body)+[0xAAFFFF]*len(suffix)
				display.set_menu(labels=prefix+body+suffix,
				                 index =len(prefix)+index,
				                 colors=colors)