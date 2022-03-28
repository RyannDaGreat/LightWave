import machine, neopixel
from esp import neopixel_write

class NeoPixel:
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3, timing=1):
        self.pin = pin
        self.n = n
        self.bpp = bpp#bytes per pixel?
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        self.timing = timing

    def __setitem__(self, index, val):
        #WARNING: This is very slow! I strongly reccomend directly editing the self.buf instead (can be over 10x faster)
        offset = index * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = val[i]

    def __getitem__(self, index):
        offset = index * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]] for i in range(self.bpp))


    def write(self):
        neopixel_write(self.pin, self.buf, self.timing)

    def display(self,buffer:bytes,start=0):
        #Give it bytes made by rgb_to_bytes. The color will be repeated, which means that sending it a solid color will set a background
        start*=self.bpp
        buffer=(buffer*(2+self.n//len(buffer)))[:self.n-start]#clip off the end
        if buffer!=self.buf[start:]:
            self.buf[start:]=buffer
            self.write()

def clamp(x,a,b):
    #assume a<b
    return min(b,max(x,a))

def rgb_to_bytes(rgb:tuple):
    #assume r,g,b are floats between 0 and 1
    r,g,b=rgb
    r=clamp(int(r*256),0,255)
    g=clamp(int(g*256),0,255)
    b=clamp(int(b*256),0,255)
    return bytes([g,r,b])#For neopixel buffers



def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    hf = int(h*6)
    hi = int(hf) % 6
    f = h - hf
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if   hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    return r, g, b

np = NeoPixel(machine.Pin(4), 100)

import utime

gtoc=utime.ticks_ms()
def tic():
    global gtoc
    gtoc=utime.ticks_ms()

def toc(s=''):
    print(s,utime.ticks_ms()-gtoc)

def demo(np):
    n = np.n
    l=[None]*100
def f():
    for i in range(1000):
        b=[(0,0,0)]*n
        w=[(50,50,50)]*n
        # for j in range(5):
            # np[j]=b
        # for j in range(5):
            # l[j]=b
        # np.write()
        # for j in range(5):
            # np[j]=w
        # for j in range(5):
            # l[j]=w
        # np.write()
        np.fill((0,0,0))
        np.write()
        np.fill((50,0,0))
        np.write()

def f(n=100):
    tic()
    for i in range(n):
        np.fill((0,0,0))
        np.write()
        np.fill((50,0,0))
        np.write()
    toc()


def g(n=100):
    tic()
    for i in range(n):
        for j in range(np.n):np[j]=(0,0,0)
        np.write()
        for j in range(np.n):np[j]=(50,0,0)
        np.write()
    toc()

def h(n=100):
    tic()
    for i in range(n):
        np.buf[:]=bytearray(bytes([0,0,0])*np.n)
        np.write()
        np.buf[:]=bytearray(bytes([50,0,0])*np.n)
        np.write()
    toc()


import utime
def h2(n=100):
    tic()
    b=(bytes([0,0,0])*np.n)
    w=(bytes([50,0,0])*np.n)
    for i in range(n):
        np.buf[:]=bytes(b)
        np.write()
        utime.sleep_us(500)
        O=bytearray(w)
        O[:i]=b'\x00'*i
        np.buf[:]=bytes(O)
        np.write()
        utime.sleep_us(100)
    toc()




import utime
def h2(n=100):
    tic()
    b=(bytes([0,0,0])*np.n)
    w=(bytes([50,0,0])*np.n)
    for i in range(n):
        O=bytearray(b)
        O[3*i%len(O)]=255
        np.buf[:]=O
        utime.sleep_us(10)
        np.write()
        continue

        O=bytearray(w)
        O[:i]=b'\x00'*i
        np.buf[:]=bytes(O)
        np.write()
        utime.sleep_us(500)
    toc()

def hh(n=100):
    tic()
    b= bytes([0,0,0])*np.n
    w=bytes([50,0,0])*np.n
    for i in range(n):
        np.buf[:]=b
        np.write()
        np.buf[:]=w
        np.write()
    toc()
    print(w)
    print(b)


    # # cycle
    # for i in range(4 * n):
    #     tic()
    #     for j in range(n):
    #         np[j] = (0, 0, 0)
    #     np[i % n] = (255, 255, 255)
    #     toc('Part 1')
    #     np.write()
    #     # time.sleep_ms(25)

    # # bounce
    # for i in range(4 * n):
    #     tic()
    #     for j in range(n):
    #         np[j] = (0, 0, 128)
    #     if (i // n) % 2 == 0:
    #         np[i % n] = (0, 0, 0)
    #     else:
    #         np[n - 1 - (i % n)] = (0, 0, 0)
    #     toc("part 2")
    #     np.write()
    #     # time.sleep_ms(60)

    # # fade in/out
    # for i in range(0, 4 * 256, 8):
    #     tic()
    #     for j in range(n):
    #         if (i // 256) % 2 == 0:
    #             val = i & 0xff
    #         else :
    #             val = 255 - (i & 0xff)
    #         np[j] = (val, 0, 0)
    #     toc('part 3')
    #     np.write()

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write() 
# demo(np)

hh()