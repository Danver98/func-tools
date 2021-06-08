import time , math
from random import choice
def gcd(a,b):
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a        
    return a
       
def bezout(a, b):
    temp = b
    q,r,x0,x1,y0,y1 = -1,-1,1,0,0,1 
    x0_prev , y0_prev = x0,y0
    while b>0:
        q = a // b
        r = a - b*q
        a = b
        b = r
        x0_prev = x0
        y0_prev = y0
        x0 = x1
        y0 = y1
        x1 = x0_prev - q * x1	
        y1 = y0_prev - q * y1
    if x0 < 0:
        return temp - abs(x0)
    return x0

def sgrow(a):
    for index,i in enumerate(a):
        sum = 0
        for el in a[:index]:
            sum+=el
            if sum >= i:
                return False
    return True


    #print(3*11 %31)

def doit(b):
    print(f"Исходный: {b}")
    ma = max(b)
    dma= 2*max(b)
    for m in range(ma+1,dma):
        for u in range(1,m):
            if gcd(u,m) == 1 and bezout(u,m) < ma:      
                a = []
                rev = bezout(u,m)
                for i in b:
                    a.append((i * u) % m)
                if sgrow(a):                   
                    print(f"u:{u} m:{m} rev(u): {rev}")
                    print(a)
            else:
                continue

def primitive(n):
    timer1 = time.time()
    for i in range(2,n):
        field_elems = [i for i in range(1,n)]
        for g in range(0,n):
            cur_el = (i**g) % n
            if cur_el in field_elems:
                field_elems.remove(cur_el)
        
        if len(field_elems) == 0:
            print(f"Подходит {i}")
            nums = []
            for g in range(0,n -1 ):
                nums.append((i**g) % n)
            print(nums)
    time_elapsed = time.time() - timer1 
    print(f"Elapsed time:{time_elapsed}")

def step_giant_step_baby():
    #11^x mod 1103 = 233
    a = 11
    p = 1103
    y = 233   
    m = math.ceil(math.sqrt(p)) + 3
    k = math.floor(math.sqrt(p))
    print("%d , %d : %d  " % (m,k, m*k))
    ym = []
    yk = []
    for i in range(1,m):
        ym.append(((a**i ) * y) % p)
    for i in range(1,k+1):
        yk.append((a**(i*m)) % p)
    print(ym)
    print(yk)
    sizem = len(ym)
    sizek = len(yk)
    num_i =0
    num_j = 0
    for i in range(0,sizem):
        for j in range(0,sizek): 
            if ym[i] == yk[j]:
                print(" elem: %d , pos: %d , j: %d " % (ym[i] , i+1 , j+1))
                num_i = i+1 
                num_j = j+1
                break
    print("X is: %d" % (num_i *m - num_j))

if __name__ == "__main__":
    step_giant_step_baby()


    
    