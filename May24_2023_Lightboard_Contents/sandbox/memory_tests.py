import gc


#If nothing happens, all three of these should print the same value
print("PART 1: Doing nothing; Should be same")
print(gc.mem_free())
print(gc.mem_free())
print(gc.mem_free())

print("PART 2: Assigning different ints to same vairable; Should stay the same")
a=10
print(gc.mem_free())
a=10
print(gc.mem_free())
a=11
print(gc.mem_free())
a=1999
print(gc.mem_free())

mem=prev_mem=0
def get_memdiff():
	global prev_mem,mem
	prev_mem=mem
	mem=gc.mem_free()
	return prev_mem-mem
get_memdiff()#Initialize mem and prev_mem

print("PART 3: Testing mem difference function; Should stay the same at 0")
print(get_memdiff())
print(get_memdiff())
print(get_memdiff())
print(get_memdiff())

print("PART 4: Creating empty dicts; Should decrease linearly")
print(gc.mem_free())
a={}
print(gc.mem_free())
b={}
print(gc.mem_free())
c={}
print(gc.mem_free())

print("PART 5: Creating empty dicts; Displaying mem diffs (CircuitPython measured 16 bytes per empty dict)")
_=get_memdiff();#Initialize mem and prev_mem
a={}
print(get_memdiff())
b={}
print(get_memdiff())
c={}
print(get_memdiff())

print("PART 6: Creating new int variables; displaying mem diffs")
_=get_memdiff();#Initialize mem and prev_mem
int_A=23498
print(get_memdiff())
int_B=234928
print(get_memdiff())
int_C=233498
print(get_memdiff())
int_D=2113498
print(get_memdiff())
int_E=231398
print(get_memdiff())
int_F=2345198
print(get_memdiff())
int_G=2143498
print(get_memdiff())
int_H=12873
print(get_memdiff())
int_I=84281
print(get_memdiff())
int_J=23498
print(get_memdiff())
int_K=234928
print(get_memdiff())
int_L=233498
print(get_memdiff())
int_M=2113498
print(get_memdiff())
int_N=231398
print(get_memdiff())
int_O=2345198
print(get_memdiff())
int_P=2143498
print(get_memdiff())
int_Q=12873
print(get_memdiff())
int_R=84281
print(get_memdiff())

print("PART 5: Creating dicts with four bytes as keys and None as values; diaplaying mem diffs")
_=get_memdiff();#Initialize mem and prev_mem
bd_a={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bd_b={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bd_c={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bd_d={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bd_e={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bd_f={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())


print("PART 5: Creating length-4 bytes and length-4 tuples")
_=get_memdiff();#Initialize mem and prev_mem
bt_a=b'abcd',(None,None,None,None)
print(get_memdiff())
bt_b=b'abcd',(None,None,None,None)
print(get_memdiff())
bt_c={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())
bt_d=b'abcd',(None,None,None,None)
print(get_memdiff())
bt_e=b'abcd',(None,None,None,None)
print(get_memdiff())
bt_f={b'a':None,b'b':None,b'c':None,b'd':None}
print(get_memdiff())

