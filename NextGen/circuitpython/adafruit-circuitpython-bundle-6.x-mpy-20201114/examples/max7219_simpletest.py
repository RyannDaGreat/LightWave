import time
from board import TX, RX, A1
import busio
import digitalio
from adafruit_max7219 import matrices

mosi = TX
clk = RX
cs = digitalio.DigitalInOut(A1)

spi = busio.SPI(clk, MOSI=mosi)

matrix = matrices.Matrix8x8(spi, cs)
while True:
    print("Cycle start")
    # all lit up
    matrix.fill(True)
    matrix.show()
    time.sleep(0.5)

    # all off
    matrix.fill(False)
    matrix.show()
    time.sleep(0.5)

    # one column of leds lit
    for i in range(8):
        matrix.pixel(1, i, 1)
    matrix.show()
    time.sleep(0.5)
    # now scroll the column to the right
    for j in range(8):
        matrix.scroll(1, 0)
        matrix.show()
        time.sleep(0.5)

    # show a string one character at a time
    adafruit = "Adafruit"
    for char in adafruit:
        matrix.fill(0)
        matrix.text(char, 0, 0)
        matrix.show()
        time.sleep(1.0)

    # scroll the last character off the display
    for i in range(8):
        matrix.scroll(-1, 0)
        matrix.show()
        time.sleep(0.5)

    # scroll a string across the display
    for pixel_position in range(len(adafruit) * 8):
        matrix.fill(0)
        matrix.text(adafruit, -pixel_position, 0)
        matrix.show()
        time.sleep(0.25)
