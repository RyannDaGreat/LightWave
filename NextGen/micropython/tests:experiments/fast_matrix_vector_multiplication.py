from urp import *
import micropython

def random_vector(n):
	from random import random
	out=[]
	for _ in range(n):
		out.append(random())
	return out

def random_matrix(n):
	from random import random
	out=[]
	for _ in range(n):
		out.append(random_vector(n))
	return out

@micropython.native
def dot(a, b):
    s = 0
    for i in range(0, len(b)):
        s += a[i] * b[i]
    return s

@micropython.native
def mul(A, b):
    return [dot(row, b) for row in A]

@micropython.native
def mul2(A,b):
	#This is faster than the next two commented ones
	l=len(b)
	out=[0.]*l
	for i in range(l):
		n=b[i]
		o=0.
		for k in A[i]:
			o+=k*n
		out[i]=o
	return out

# @micropython.native
# def mul2(A,b):
# 	out=[]
# 	for n,r in zip(b,A):
# 		o=0.
# 		for k in r:
# 			o+=k*n
# 		out.append(o)
# 	return o

# @micropython.native
# def mul2(A,b):
# 	out=[]
# 	for i in range(len(b)):
# 		n=b[i]
# 		o=0.
# 		for k in A[i]:
# 			o+=k*n
# 		out.append(o)
# 	return o

n=30
A=random_matrix(n)
b=random_vector(n)

_=tic()
_=mul(A,b)
_=print(toc())

_=tic()
_=mul2(A,b)
_=print(toc())

_=tic()
_=mul(A,b)
_=print(toc())

_=tic()
_=mul2(A,b)
_=print(toc())


