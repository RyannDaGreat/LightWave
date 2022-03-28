####NOTE: When doing calibration, use MEDIANS and NOT MEANS. There are spikes in the data that will mess everything up...

from sys import stdout


# # while True:
# for i in range(1000):
#     r=ms.readline()
#     if r is not None:
#         print(r.decode())
#         o=r
#         # stdout.write(r)

def handle_byteline(byteline:bytes):
    try:
        print(line.decode())
    except UnicodeError:
        #Decoding failed, could be becaue of serial problem
        pass

class LineReader:
    def __init__(self,line_handler=lambda line:print(line.decode())):
        self.buffer=b''
        self.line_handler=line_handler
    def process(self,data:bytes)->None:
        #TODO: Implement a circular buffer (make a circular buffer class implementing the buffer interface and using arrayview and bytearray) so that the garbage collector is never called and we can never run out of memory...
        #...but for now, this is efficient enough. 
        assert isinstance(data,bytes),'LineReader.process takes bytes, but got type(data)=='+repr(type(data))
        self.buffer+=data
        while True:
            index=self.buffer.find(b'\n')
            if index==-1:
                #No newlines are currently in the buffer...
                break
            self.line_handler(self.buffer[:index])
            self.buffer=self.buffer[index+1:]

# Set up the interrupt for the Nano reader...
from machine import UART,Pin
_nano_baudrate=115200
_nano_serial=UART(1,baudrate=_nano_baudrate)#UART(id)
_nano_serial.init(  baudrate=_nano_baudrate,rx=9,tx=10)#9=D2, 10=D3 (on the ESP32 board)
_nano_line_reader=LineReader()

def _process_nano_message(data:bytes):
    assert not b'\n' in data,'_process_nano_message: data should be a single line, but got data='+repr(data) # This data should be a single line, resulting from the line_handler



def process_nano_reading():
    # This method should be called frequently. Currently we don't have hardware interrupts from the Nano, so this should be done in a loop.
    data=_nano_serial.read()
    if data is not None:
        _nano_line_reader.process(data)

while True:
    process_nano_reading()
