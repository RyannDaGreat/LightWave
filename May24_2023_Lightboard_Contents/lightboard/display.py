import board
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_st7789 import ST7789
from micropython import const

import digitalio

led = digitalio.DigitalInOut(board.D5)
led.switch_to_output()
led.value=True

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D10
tft_dc = board.D9

ROTATION=180#0,90,180,270
WIDTH=320
HEIGHT=240
if not ROTATION%180:
	HEIGHT,WIDTH=WIDTH,HEIGHT

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D6)

display = ST7789(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION, auto_refresh=False)

# Make the display context
text_splash = displayio.Group(scale=1)
display.show(text_splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x0000FF  # Bright Blue

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
text_splash.append(bg_sprite)

# Draw a smaller inner rectangle
BORDER_THICKNESS=const(10)
inner_bitmap = displayio.Bitmap(WIDTH-BORDER_THICKNESS*2, HEIGHT-BORDER_THICKNESS*2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER_THICKNESS, y=BORDER_THICKNESS)
text_splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=1, x=25, y=25)
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)#512 is probably good enough for most purposes...but 1024 can fill the entire screen AND more...512 cannot...1024 takes about 4kb more memory than 512.
text_group.append(text_area)  # Subgroup for text scaling
text_splash.append(text_group)

# text_area2 = label.Label(terminalio.FONT, text="GRUMBO", y=25, color=0xFFFFFF)#512 is probably good enough for most purposes...but 1024 can fill the entire screen AND more...512 cannot...1024 takes about 4kb more memory than 512.
# text_splash.append(text_area2)  # Subgroup for text scaling
# menu_splash = displayio.Group()
menu_splash = text_splash
MENU_FONT=terminalio.FONT
MENU_FONT_WIDTH,MENU_FONT_HEIGHT=MENU_FONT.get_bounding_box()
MENU_MAX_LINES=30
MENU_LINE_SPACING=0 #Empty space between lines, in number of pixels
MENU_X_ORIGIN=15
MENU_Y_ORIGIN=25
menu_labels=[]
MENU_CURSOR_X=5
MENU_CURSOR_Y_OFFSET=-4
def _menu_calculate_y(index):
	return MENU_Y_ORIGIN+index*(MENU_FONT_HEIGHT+MENU_LINE_SPACING)

for i in range(MENU_MAX_LINES):
	label_x=MENU_X_ORIGIN
	label_y=_menu_calculate_y(i)
	menu_label = label.Label(MENU_FONT,
	                         text='',
	                         color=0xFFFFFF,
	                         x=label_x,
	                         y=label_y)
	menu_splash.append(menu_label)
	menu_labels.append(menu_label)

menu_cursor=Circle(MENU_CURSOR_X,label_y,r=4,fill=0xFFFF00)
menu_splash.append(menu_cursor)


def _menu_cursor_is_visible():
	return not menu_cursor.hidden
def _menu_cursor_set_visible(value:bool):
	if value==_menu_cursor_is_visible():
		return
	if value:
		menu_cursor.hidden=False
	else:
		menu_cursor.hidden=True
_menu_cursor_set_visible(False)
def set_menu_cursor_index(index,refresh=True):
	if index is None:
		_menu_cursor_set_visible(False)
	else:
		_menu_cursor_set_visible(True)
		new_y=_menu_calculate_y(index)+MENU_CURSOR_Y_OFFSET
		if menu_cursor.y!=new_y:
			menu_cursor.y=new_y
	if refresh:
		display.refresh()

def refresh():
	display.refresh()

display_mode='text' #text, menu

#INTERFACE IS SUBJECT TO MAJOR CHANGES SOON
def set_text(text:str,refresh=True):
	#TODO: Get rid of 'display_mode' and its distinction between set_text and set_menu. They're unified now.
	set_menu(text.split('\n'))
	return


	# global display_mode
	# if display_mode!='text':
	# 	set_menu([],refresh=False)
	# 	display_mode='text'
	# text_area.text=text
	# if refresh:
	# 	display.refresh()

class TemporarySetText:
	#WARNING: This should not be used until the entire display works...it won't revert back to a menu afterwards so what good is it?
	def __init__(self,text=None):
		self.text=text
	def __enter__(self):
		self.old_text=text_area.text
		if self.text is not None:
			set_text(self.text,refresh=False)
	def __exit__(self,*args):
		set_text(self.old_text,refresh=False)

######################### EFFICIENT MENU DISPLAYS ############################

# Make the display context
# menu_splash = text_splash#displayio.Group()

# MENU_MAX_LINES=12
# MENU_LINE_SPACING=10
# MENU_X_ORIGIN=25
# MENU_Y_ORIGIN=25
# menu_labels=[]
# for i in range(MENU_MAX_LINES):
# 	print("SHOWING",i)
# 	# menu_labels.append(menu_label)
# 	menu_splash.append(menu_label)
# 	display.refresh()


# while True:pass

def set_menu(labels,index:int=None,colors=None,refresh=True):
	#labels is list of strs
	#colors is list of ints
	assert len(labels)<=MENU_MAX_LINES
	labels=tuple(labels)
	labels=tuple(str(x) for x in labels)
	if colors is None:
		colors=tuple(0xFFFFFF for menu_label in menu_labels)
	colors=list(colors)
	while len(colors)<len(menu_labels):
		colors.append(0xFFFFFF)
	global display_mode
	if display_mode!='menu':
		# displayio.release_displays()
		# display.show(menu_splash)
		text_area.text=''#TODO: Implement set_text with set_menu to make it faster when multiple lines are the same...
		display_mode='menu'
	for label in labels:
		assert isinstance(label,str),'Label should be string but got type '+repr(type(label))
		assert '\n' not in label,'Menu labels can only be one line. Anything else is too ugly to bear...'
	for i,label in enumerate(labels+('',)*(len(menu_labels)-len(labels))):
		# print(i,len(menu_labels),len(labels),'CHUNKER')
		color=colors[i]
		if menu_labels[i].text!=label:
			#Only change the ones that need to be changed...
			menu_labels[i].text=label
		if menu_labels[i].color!=color:
			menu_labels[i].color=color
	set_menu_cursor_index(index,refresh=True)
	if refresh:
		display.refresh()

# while True:

	# print(lightboard_select(['Hello','World','How','Is','Life']))

# def lines(i=0):
# 	w=30
# 	h=MENU_MAX_LINES-1
# 	lines=[('-' if i%2 else '-')*w]*h
# 	lines.insert(i,'i'*w)
# 	return '\n'.join(lines)


# set_menu(('||`,yIg'*10,)*10)
# # while True:pass

# # while True:
# # 	for i in range(3):
# # 		print(i,'CHUMP')
# # 		set_text(lines(i))



# while True:
# 	for i in range(MENU_MAX_LINES):
# 		from time import sleep
# 		print('mennu',i)
# 		set_menu_cursor_index(i)
# 		sleep(1/60)


# # while True:
# 	for i in range(MENU_MAX_LINES):
# 		print(i)
# 		colors=[0xFFFFFF]*MENU_MAX_LINES
# 		colors[i]=0xFF00FF
# 		set_menu(lines(i).split('\n'),colors)
# 		display.refresh()


# def set_menu_options(selected_index,prompt,options):
# 	pass




