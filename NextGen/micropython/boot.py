#Ryan Burgert 2019
#Mount the SD card to the microcontroller

import os, machine, sdcard, sys
from machine import Pin,SPI

#For information about SPI in micropython, see https://docs.micropython.org/en/latest/library/machine.SPI.html#machine-spi

if sys.platform=='esp32':
    #ONLY FOR ESP32
    #Currently, I'm using bit-banging to read from the SD (not very efficient, but I finally got it to work on the ESP32!)
    sd_spi=SPI(-1,sck=Pin(32),miso=Pin(34),mosi=Pin(26))#id=-1 indicates we're going to use bit-banging instead of hardware SPI.
    sd = sdcard.SDCard(spi=sd_spi,cs=Pin(33))  # hard reset required after wiring
else:
    #ONLY FOR ESP8266
    sd = sdcard.SDCard(SPI(1),Pin(15))  # hard reset required after wiring

vfs = os.VfsFat(sd)   # is this required?
os.umount('/')
os.mount(vfs,'/')   # or '/' if you did the umount command before