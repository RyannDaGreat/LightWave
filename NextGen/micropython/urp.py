#Micro rp: uRP (rp for micropython)
import utime

def millis()->int:
	#Return the global time in milliseconds (returns an integer)
	return utime.ticks_ms()



#region Tic,Toc
def gtoc()->float:
    #Return time in seconds as a floating point (time.time returns an integer)
    return utime.ticks_us()/10**6
_global_tic=gtoc()

def tic() -> callable:
    global _global_tic
    _global_tic=local_tic=gtoc()
    def local_toc():  # Gives a permanent toc to this tic, specifically
        return gtoc() - local_tic
    return local_toc  # Returns a method so you can do a=tic();a.toc() ⟵ Gives a local (not global) toc value so each tic can be used as a new timer

def toc() -> float:
    return gtoc() - _global_tic

def ptoc(new_line=True) -> None:
    print(str(toc()) + " seconds",end='\n'if new_line else '')

def ptoctic(label='') -> None:
    print(label,end='')
    ptoc()
    tic()
#endregion

def run_as_new_thread(function,*args,**kwargs):
	#I think this only works in the esp32...
	#https://docs.python.org/3/library/_thread.html
	from _thread import start_new_thread
	start_new_thread(function,args,kwargs)

def unicode_loading_bar(n,chars='▏▎▍▌▋▊▉█'):
    """
    #EXAMPLE 1: for _ in range(200):print(end='\r'+unicode_loading_bar(_));sleep(.05)
    #EXAMPLE 2:
    #    for _ in range(1500):
   	#        import math
   	#        from time import sleep
    #        sleep(1/30)#30fps
    #        tau=6.283185307179586
    #        x=_/1000#_ is between 0 and 1
    #        x**=2#Frequency increases over time
    #        x*=tau
    #        x*=10
    #        x=math.sin(x)
    #        x+=1#Make it all positive
    #        x*=20
    #        x*=8
    #        print(unicode_loading_bar(x))
    #THE ABOVE EXAMPLE PRINTS SOMETHING LIKE THIS:
    # ▊
    # █▊
    # ███▏
    # ████▌
    # ██████▏
    # ███████▊
    # █████████▍
    # ██████████▋
    # ███████████▋
    # ████████████▎
    # ████████████▌
    # ████████████▍
    # ███████████▊
    # ██████████▊
    # █████████▍
    # ███████▉
    # ██████▏
    # ████▋
    # ███
    # █▊
    # ▊
    # ▎
    # ▏
    # ▍
    # █
    # ██
    # ███▎
    """

    assert n>=0,'Input assumption'
    assert isinstance(chars,str),'Input assumption'
    assert len(chars)>=1,'Input assumption'
    n=int(n)
    n=max(0,n)#Clip off negative numbers
    size=len(chars)
    output =n//size*chars[-1]
    output+=chars[n%size]
    return output