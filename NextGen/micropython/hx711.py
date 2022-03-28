#LoPy implementation, found on github: https://github.com/robert-hh/hx711-lopy

from machine import Pin, enable_irq, disable_irq, idle, SPI



class HX711:
    def __init__(self, dout, pd_sck, gain=128):

        self.pSCK = Pin(pd_sck, mode=Pin.OUT)
        self.pOUT = Pin(dout, mode=Pin.IN, pull=Pin.PULL_UP)
        self.pSCK.value(False)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.1
        self.filtered = 0

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        self.read()
        self.filtered = self.read()
        # print('Gain & initial value set') #Wtf? Why did they decide to print out to the serial port? That could mess stuff up...

    def is_ready(self):
        return self.pOUT() == 0

    def read(self):
        # wait for the device being ready
        while self.pOUT() == 1:
            idle()

        # shift in data, and gain & channel info
        result = 0
        for j in range(24 + self.GAIN):
            state = disable_irq()
            self.pSCK(True)
            self.pSCK(False)
            enable_irq(state)
            result = (result << 1) | self.pOUT()

        # shift back the extra bits
        result >>= self.GAIN

        # check sign
        if result > 0x7fffff:
            result -= 0x1000000

        return result

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self, times=3):
        return self.read_average(times) - self.OFFSET

    def get_units(self, times=3):
        return self.get_value(times) / self.SCALE

    def tare(self, times=15):
        sum = self.read_average(times)
        self.set_offset(sum)

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant=None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)


class Ryan_HX711(HX711):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        #Defaults. Should probably be loaded from some database later for every load cell.
        self.tare_value=0
        self.grams_per_value=1
        self.start_auto_average_read()

    def set_read_interrupt(self,handler=None):
        #the handler function should accept an integer and return whatever (it doesn't matter what it returns)
        #if handler is None, it will disable the interrupt
        def wrapper(_):

            if self.pOUT():
                #Exactly one half of the time, it will return not be self.ready() (inlined for efficiency). I don't know why though; I'm not that interested tbh
                return

            #Copied the guts of the original read function into here (inlined it)
            # shift in data, and gain & channel info
            result = 0

            state = disable_irq()
            for _ in range(24 + self.GAIN):
                self.pSCK(True)
                self.pSCK(False)
                result = (result << 1) | self.pOUT()
            enable_irq(state)

            # shift back the extra bits
            result >>= self.GAIN

            # check sign
            if result > 0x7fffff:
                result -= 0x1000000

            handler(result)

        if handler is None:
            #Disable the interrupt by passing handler=None
            wrapper=None

        self.pOUT.irq(handler=wrapper,trigger=Pin.IRQ_FALLING)

    # def start_auto_raw_read(self):
    #     #Call this if you want to use self._value
    #     #Slightly faster than start_auto_average_read, but I haven't actually tested the speed difference (it's probably negligible)
    #     self._value=0
    #     def handler(value):
    #         self._value=value
    #     self.set_read_interrupt(handler)

    def start_auto_average_read(self):
        #Call this if you want to use self.average (which will accuulate an average value over time until observed, getting more accurate)
        self._average_sum=0
        self._average_count=0
        self._average_was_oberserved=False
        self._value=0
        def handler(value):
            self._value=value
            if self._average_was_oberserved:
                self._average_was_oberserved=False
                self._average_count=0
                self._average_sum=0
            self._average_count+=1
            self._average_sum+=value
        self.set_read_interrupt(handler)

    def calibrate(self):
        self.set_read_interrupt(None)#Pause auto-read for a little while...
        input("Please take everything off the scale. Press enter when ready to start the tare.")
        print(end="Starting tare...please don't touch the scale for about 10 seconds...")
        self.tare_value=self.read_average(800)#80 hz and 800 samples = 10 seconds
        print("done. Average raw value during tare was "+str(self.tare_value))
        print("Please place a mass on the scale, and enter it's mass in grams.")
        actual_mass=eval(input("Mass in grams: "))
        print("Please wait about 10 seconds, don't touch the scale...")
        observed_value=self.read_average(800)
        observed_difference=observed_value-self.tare_value
        self.grams_per_value=actual_mass/observed_difference
        print("The observed value was "+str(observed_value)+", which is supposed to be equivalent "+str(actual_mass)+" grams")
        print("The grams_per_value coefficient is calculated to be "+str(self.grams_per_value))
        print("The conversion between value and grams is grams=(value-("+str(self.tare_value)+"))*"+str(self.grams_per_value))
        self.start_auto_average_read()#Start auto-read back up again...

    def value_to_grams(self,value):
        #Value is an integer reading we get from the hx711
        return (value-self.tare_value)*self.grams_per_value

    @property
    def value(self):
        return self._value

    @property
    def grams(self):
        return self.value_to_grams(self._value)
    

    @property
    def average_value(self):
        #The longer you wait before between observing this property, the more accurate each observation will be
        state = disable_irq()
        self._average_was_oberserved=True
        out=self._average_sum/self._average_count
        enable_irq(state)
        return out

    @property
    def average_grams(self):
        return self.value_to_grams(self.average_value)



#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################





class SPI_HX711:
    def __init__(self, dout, pd_sck, spi_clk=0, gain=128):
        #By default, pin 0 is a throwaway pin :(

        self.pSCK = Pin(pd_sck, mode=Pin.OUT)
        self.pOUT = Pin(dout, mode=Pin.IN, pull=Pin.PULL_UP)
        # self.spi = SPI(0, baudrate=1000000, polarity=0,phase=0, pins=(spi_clk, pd_sck, dout))
        # self.spi = SPI(-1, mode=SPI.MASTER, baudrate=1000000, polarity=0,phase=0, pins=(spi_clk, pd_sck, dout))
        self.spi=SPI(-1, baudrate=1000000, polarity=0,phase=0,sck=Pin(pd_sck),mosi=Pin(dout),miso=Pin(spi_clk))
        self.pSCK(0)

        self.clock_25 = b'\xaa\xaa\xaa\xaa\xaa\xaa\x80'
        self.clock_26 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa0'
        self.clock_27 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa8'
        self.clock = self.clock_25
        self.lookup = (b'\x00\x01\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x04\x05\x00\x00\x06\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x08\x09\x00\x00\x0a\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x0c\x0d\x00\x00\x0e\x0f')
        self.in_data = bytearray(7)

        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.1
        self.filtered = 0

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain is 128:
            self.clock = self.clock_25
        elif gain is 64:
            self.clock = self.clock_27
        elif gain is 32:
            self.clock = self.clock_26

        self.read()
        self.filtered = self.read()
        print('Gain & initial value set')

    def read(self):
        # wait for the device to get ready
        while self.pOUT() != 0:
            idle()

        # get the data and set channel and gain
        self.spi.write_readinto(self.clock, self.in_data)

        # pack the data into a single value
        result = 0
        for _ in range(6):
            result = (result << 4) + self.lookup[self.in_data[_] & 0x55]

        # return sign corrected result
        return result - ((result & 0x800000) << 1)

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.read_lowpass() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant=None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)

class Ryan_SPI_HX711(SPI_HX711):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        #Defaults. Should probably be loaded from some database later for every load cell.
        self.tare_value=0
        self.grams_per_value=1
        self.start_auto_average_read()

    def set_read_interrupt(self,handler=None):
        #the handler function should accept an integer and return whatever (it doesn't matter what it returns)
        #if handler is None, it will disable the interrupt
        def wrapper(_):

            if self.pOUT():
                #Exactly one half of the time, it will return not be self.ready() (inlined for efficiency). I don't know why though; I'm not that interested tbh
                return

            self.spi.write_readinto(self.clock, self.in_data)

            # pack the data into a single value
            result = 0
            for _ in range(6):
                result = (result << 4) + self.lookup[self.in_data[_] & 0x55]

            # return sign corrected result
            result = result - ((result & 0x800000) << 1)

            handler(result)

        if handler is None:
            #Disable the interrupt by passing handler=None
            wrapper=None

        self.pOUT.irq(handler=wrapper,trigger=Pin.IRQ_FALLING)

    # def start_auto_raw_read(self):
    #     #Call this if you want to use self._value
    #     #Slightly faster than start_auto_average_read, but I haven't actually tested the speed difference (it's probably negligible)
    #     self._value=0
    #     def handler(value):
    #         self._value=value
    #     self.set_read_interrupt(handler)

    def start_auto_average_read(self):
        #Call this if you want to use self.average (which will accuulate an average value over time until observed, getting more accurate)
        self._average_sum=0
        self._average_count=0
        self._average_was_oberserved=False
        self._value=0
        def handler(value):
            self._value=value
            if self._average_was_oberserved:
                self._average_was_oberserved=False
                self._average_count=0
                self._average_sum=0
            self._average_count+=1
            self._average_sum+=value
        self.set_read_interrupt(handler)

    def calibrate(self):
        self.set_read_interrupt(None)#Pause auto-read for a little while...
        input("Please take everything off the scale. Press enter when ready to start the tare.")
        print(end="Starting tare...please don't touch the scale for about 10 seconds...")
        self.tare_value=self.read_average(800)#80 hz and 800 samples = 10 seconds
        print("done. Average raw value during tare was "+str(self.tare_value))
        print("Please place a mass on the scale, and enter it's mass in grams.")
        actual_mass=eval(input("Mass in grams: "))
        print("Please wait about 10 seconds, don't touch the scale...")
        observed_value=self.read_average(800)
        observed_difference=observed_value-self.tare_value
        self.grams_per_value=actual_mass/observed_difference
        print("The observed value was "+str(observed_value)+", which is supposed to be equivalent "+str(actual_mass)+" grams")
        print("The grams_per_value coefficient is calculated to be "+str(self.grams_per_value))
        print("The conversion between value and grams is grams=(value-("+str(self.tare_value)+"))*"+str(self.grams_per_value))
        self.start_auto_average_read()#Start auto-read back up again...

    def value_to_grams(self,value):
        #Value is an integer reading we get from the hx711
        return (value-self.tare_value)*self.grams_per_value

    @property
    def value(self):
        return self._value

    @property
    def grams(self):
        return self.value_to_grams(self._value)
    

    @property
    def average_value(self):
        #The longer you wait before between observing this property, the more accurate each observation will be
        state = disable_irq()
        self._average_was_oberserved=True
        out=self._average_sum/self._average_count
        enable_irq(state)
        return out

    @property
    def average_grams(self):
        return self.value_to_grams(self.average_value)





