












# import digitalio
# from board import *
# import time

# led = digitalio.DigitalInOut(D17)
# led.direction = digitalio.Direction.OUTPUT

# wip = digitalio.DigitalInOut(D16)
# wip.direction = digitalio.Direction.OUTPUT

# from urp import *

# # assert False

# t=.01
# b=True
# while True:
#     led.value = True
#     time.sleep(t)
#     led.value = False
#     time.sleep(t)
#     if toc()>.1:
#     	b+=1
#     	b%=3
#     	wip.value=bool(b)
#     	print('B',b)
#     	tic()























# from urp import *
# import time
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.ads1x15 import Mode
# from adafruit_ads1x15.analog_in import AnalogIn

# # Data collection setup
# RATE = 860

# # Create the I2C bus with a fast frequency
# if 'i2c' not in dir():
#     i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# ads = ADS.ADS1115(i2c)
# ads.gain=8

# # Create single-ended input on channel 0
# chan0 = AnalogIn(ads, ADS.P0)
# chan1 = AnalogIn(ads, ADS.P1)
# chan2 = AnalogIn(ads, ADS.P2)

# # ADC Configuration
# # ads.mode = Mode.CONTINUOUS #Disabled because we can't do this :(( big sad. However, if we only want one output it IS possible to use continuous...but I want generalizability...
# ads.data_rate = RATE

# N=1000
# V=[]

# def mean(l):
#     l=list(l)
#     return sum(l)/len(l)

# def std(l):
#     u=mean(l)
#     return mean((x-u)**2 for x in l)**.5

# while True:
#     v=chan0.value
#     v=chan0.value
#     v=chan0.value
#     v=chan0.value
#     V.append(v)
#     while len(V)>N:
#         del V[0]
#     print(v,32767-chan1.value)
#     # print(v,32767-chan1.value,0,32767)
#     # print(v,'\tstd:',std(V),'\tmean:',mean(V))

# # 26334/2 = 13167

# #The stamdard deviation at 1x is about .6 to .75 (out of , which is about 5x less than the std
# # 3.3*32768/26334=4.10626566416 ~= 4.096 (thte 1x amp)
# # Therefore, the max for 

# #STANDARD DEVIATIONS VS GAIN:
# #   1: ?    to 0.80  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
# #   2: ?    to 0.87  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
# #   4: ?    to 1.16  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
# #   8: ?    to 1.82  (? because haven't bothered to find lower bound yet; it depends on the voltage input)
# #  16: 2.72 to 3.75












 


# # CircuitPython demo - NeoPixel
# import time
# import board
# import neopixel

# pixel_pin = board.A1
# num_pixels = 119

# pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=.1, auto_write=False)


# def wheel(pos):
#     # Input a value 0 to 255 to get a color value.
#     # The colours are a transition r - g - b - back to r.
#     if pos < 0 or pos > 255:
#         return (0, 0, 0)
#     if pos < 85:
#         return (255 - pos * 3, pos * 3, 0)
#     if pos < 170:
#         pos -= 85
#         return (0, 255 - pos * 3, pos * 3)
#     pos -= 170
#     return (pos * 3, 0, 255 - pos * 3)


# def color_chase(color, wait):
#     for i in range(num_pixels):
#         pixels[i] = color
#         time.sleep(wait)
#         pixels.brightness=random()
#         pixels.show()
#     # time.sleep(0.5)

# from random import random

# import analogio
# from board import *
# adc=analogio.AnalogIn(A6)
# from time import sleep
# # for i in range(5000000):
# #     sleep(.0)
# #     print(adc.value/2**16)


# def pixel_height():
#     v=(adc.value/2**16)
#     print(v)
#     return int(v*num_pixels)


# def rainbow_cycle(wait):
#     for j in range(255):
#         pixels.fill((0,0,0))
#         for i in range(pixel_height()):
#             rc_index = (i * 256 // num_pixels) + j
#             pixels[i] = wheel(rc_index & 255)
#         # pixels.brightness=random()
#         pixels.show()
#         time.sleep(wait)


# RED = (255, 0, 0)
# YELLOW = (255, 150, 0)
# GREEN = (0, 255, 0)
# CYAN = (0, 255, 255)
# BLUE = (0, 0, 255)
# PURPLE = (180, 0, 255)


# from time import monotonic_ns
# def millis():
#     return monotonic_ns()//1000000
# def seconds():
#     return monotonic_ns() /1000000000
# _mtoc=millis()
# def mtic():
#     global _mtoc
#     now=millis()
#     out=now-_mtoc
#     _mtoc=now
#     return out
# def mtoc():
#     now=millis()
#     return now-_mtoc
# def mptoctic(*msg):
#     print(*(msg+('TOC:',mtoc(),'millis')))
#     mtic()


# def f():

#     print("GOGO ")
#     pixels.fill(RED)
#     pixels.show()
#     print("POD ")
#     # Increase or decrease to change the speed of the solid color change.
#     time.sleep(1)
#     mptoctic("Greenstart")
#     pixels.fill((255,255,255))
#     mptoctic("Greenend")
#     pixels.show()
#     time.sleep(5)
#     pixels.fill(BLUE)
#     print("sloggo ")
#     pixels.show()
#     time.sleep(1)

#     color_chase(RED, 0.00)  # Increase the number to slow down the color chase
#     color_chase(YELLOW, 0.000)
#     print("miranada ")
#     color_chase(GREEN, 0.00)
#     color_chase(CYAN, 0.00)
#     color_chase(BLUE, 0.00)
#     print("porky ")
#     color_chase(PURPLE, 0.00)

#     rainbow_cycle(0)  # Increase the number to slow down the rainbow
# # f()
# # pixels.brightness=
# # while True:
#     # rainbow_cycle(0)

# pixels.fill((0,0,0))
# # pixels.fill(RED)
# for i in range(100):
#     pixels.fill((0,0,0))
#     rainbow_cycle(0)