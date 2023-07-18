
#Please use the antennae! it makes it much better.
"""
Simple example of using the RF24 class.
"""
import time
import struct
import board
import digitalio
from urp import *
from time import sleep

# if running this on a ATSAMD21 M0 based board
# from circuitpython_nrf24l01.rf24_lite import RF24
from circuitpython_nrf24l01.rf24 import RF24

# change these (digital output) pins accordingly
LIGHTBOARD=True
if LIGHTBOARD:
	ce = digitalio.DigitalInOut(board.D21)
	csn = digitalio.DigitalInOut(board.D20)
else:
	ce = digitalio.DigitalInOut(board.D9)
	csn = digitalio.DigitalInOut(board.D14)

# using board.SPI() automatically selects the MCU's
# available SPI pins, board.SCK, board.MOSI, board.MISO
spi = board.SPI()  # init spi bus object

# we'll be using the dynamic payload size feature (enabled by default)
# initialize the nRF24L01 on the spi bus object
nrf = RF24(spi, csn, ce)

# set the Power Amplifier level to -12 dBm since this test example is
# usually run with nRF24L01 transceivers in close proximity
nrf.pa_level = 0

nrf.data_rate=1#1:1mbps, 2:2mbps

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

# to use different addresses on a pair of radios, we need a variable to
# uniquely identify which address this radio will use to transmit
# 0 uses address[0] to transmit, 1 uses address[1] to transmit
radio_number = LIGHTBOARD

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1


def master():  # count = 5 will only transmit 5 packets
	"""Transmits an incrementing integer every second"""
	nrf.listen = False  # ensures the nRF24L01 is in TX mode
	i=0
	while True:
		tic()
		i+=1
		msg='%.6f \t#%i'%(gtoc(),i)
		# result=nrf.send(msg.encode())
		result=nrf.send(bytes([0x90,0x3c,0x40]))
		print(result)
		sleep(.25)
		# ptoc()


def slave():
	nrf.listen = True  # put radio into RX mode and power up
	while True:
		if nrf.available():
			# grab information about the received payload
			payload_size, pipe_number = (nrf.any(), nrf.pipe)
			# fetch 1 payload from RX FIFO
			buffer = nrf.read()  # also clears nrf.irq_dr status flag
			try:
				print(buffer)
			except UnicodeError:
				print("(Cant print)")

if LIGHTBOARD:
	master()
else:
	slave()

