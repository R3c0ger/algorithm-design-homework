import  sys
#初始化参数：
#设定初始值，这些值是固定的，由SM3标准规定。
#变量A B C D E F G H
IV = ['7380166f', '4914b2b9', '172442d7', 'da8a0600','a96f30bc', '163138aa', 'e38dee4d', 'b0fb0e4e']

#Tj常量
def T(j):  #OK
    if j in range(0,16):
        return '79cc4519'
    elif j in range(16,64):
        return '7a879d8a'
    else:
        exit()

#填充与分组
def pad_and_group(m):   #OK
    m_length = len(m)
    m += '8'    #填充1000,感觉是有点不严谨的，补一
    tmp = len(m)%128 #512/4=128
    m += (112 - tmp)%128 *'0'  #448/4=112,补零,112小于tmp的情况，所以要取余
    m += hex(m_length*4)[2:].zfill(16) #补长度64bit，16个十六进制数
    B = []
    for i in range(0,len(m),128):
        B.append(m[i:i+128])
    return B

#异或运算(32bit位的异或，字与字)
def Xor(a,b):    #OK
    a = int(a, 16)
    b = int(b, 16)
    tmp = '{:08x}'.format(a ^ b)
    return tmp

#与运算(32bit位的与，字与字)
def And(a,b):   #OK
    a = int(a, 16)
    b = int(b, 16)
    tmp = '{:08x}'.format(a & b)
    return tmp

#或运算
def Or(a,b):   #OK
    a = int(a, 16)
    b = int(b, 16)
    tmp = '{:08x}'.format(a | b)
    return tmp

#非运算(32bit位的非)
def Not(a):    #OK
    a_bin = ''.join(bin(int(i,16))[2:].zfill(4) for i in a)
    tmp =  ''.join(str(abs(int(i)-1)) for i in a_bin)
    a_hex = ''.join(hex(int(tmp[i:i + 4], 2))[2:] for i in range(0, len(tmp), 4))
    return a_hex

#加运算(32bit位的加)
def Add(x,y):   #OK
    a = int(x, 16)
    b = int(y, 16)
    tmp = (a + b) % pow(2, 32)
    tmp = '{:08x}'.format(tmp)
    return tmp

#循环左移(32bit的循环左移n位)
def left_shift(a,n):    #OK
    a_bin = ''.join(bin(int(i,16))[2:].zfill(4) for i in a)
    n = n%32
    a_bin = a_bin[n:] + a_bin[:n]
    a_hex = ''.join(hex(int(a_bin[i:i+4],2))[2:] for i in range(0,len(a_bin),4))
    return a_hex

#置换函数
def P0(x):   #OK
    b = Xor(x,left_shift(x,9))
    c = Xor(b,left_shift(x,17))
    return c

def P1(x):   #OK
    b = Xor(x, left_shift(x, 15))
    c = Xor(b, left_shift(x, 23))
    return c

#布尔函数
def FF(x,y,z,j):   #OK
    if j in range(0,16):
        a = Xor(x,y)
        return Xor(a,z)
    elif j in range(16,64):
        x_y = And(x,y)
        x_z = And(x,z)
        y_z = And(y,z)
        a = Or(x_y,x_z)
        return Or(a,y_z)

def GG(x,y,z,j):  #OK
    if j in range(0, 16):
        a = Xor(x, y)
        return Xor(a, z)
    elif j in range(16, 64):
        a = And(x,y)
        b = And(Not(x),z)
        return Or(a,b)

#扩展(将块扩展为132个字，68+64个)
def expand(B):    #OK
    W1 = ['0' for i in range(68)]
    W2 = ['0' for i in range(64)]
    for i in range(0,128,8): #前十六个字
        W1[i//8] = B[i:i+8]
    for i in range(16,68):
        tmp = Xor(W1[i-16], W1[i-9])
        tmp = Xor(tmp, left_shift(W1[i-3],15))
        tmp = P1(tmp)
        b = left_shift(W1[i-13],7)
        tmp = Xor(tmp,b)
        tmp = Xor(tmp, W1[i-6])
        W1[i] = tmp
    for i in range(64):
        W2[i] = Xor(W1[i],W1[i+4])
    return W1,W2

#压缩函数，B为各个消息块，即512bit，V为V[k]的数组，V[k]存的值为ABCDEFGH
def CF(V,Bi):
    A = V[0]
    B = V[1]
    C = V[2]
    D = V[3]
    E = V[4]
    F = V[5]
    G = V[6]
    H = V[7]
    W1,W2 = expand(Bi)
    for j in range(64):
        a = left_shift(A,12)
        b = left_shift(T(j), j % 32)
        tmp = Add(a,E)
        tmp = Add(tmp,b)
        SS1 = left_shift(tmp,7)
        SS2 = Xor(SS1,a)
        c = FF(A,B,C,j)
        tmp = Add(c,D)
        tmp = Add(tmp,SS2)
        TT1 = Add(tmp,W2[j])
        d = GG(E,F,G,j)
        tmp = Add(d,H)
        tmp = Add(tmp,SS1)
        TT2 = Add(tmp,W1[j])
        D = C
        C = left_shift(B,9)
        B = A
        A = TT1
        H = G
        G = left_shift(F,19)
        F = E
        E = P0(TT2)
    result_str = A+' '+B+' '+C+' '+D+' '+E+' '+F+' '+G+' '+H
    tmp = result_str.split(' ')
    result = [Xor(tmp[i],V[i]) for i in range(len(tmp))]
    return result

def sm3(m):
    hex_message = m.hex()
    B = pad_and_group(hex_message)
    V = [[] for i in range(len(B)+1)]  #用于迭代
    V[0] = IV
    for i in range(len(B)):
        V[i+1] = CF(V[i],B[i])
    return ''.join(V[-1])

def signature(m,key):
    # key = bytes(key,'utf-8')
    tmp = m + key
    return m.hex() + '.' + sm3(tmp)

#迭代压缩
if __name__ == "__main__":
    secret_key = 'helloworld'
    if len(sys.argv) == 3:
        message = sys.argv[1].encode('utf-8')
        secret_key = sys.argv[2].encode('utf-8')
        print("签名后的数据流：\n" + signature(message,secret_key))
    elif len(sys.argv) == 2:
        message = sys.argv[1].encode('utf-8')
        print("签名后的数据流：\n" + signature(message,secret_key))
    else:
        print("命令行使用方式如下：\n"
              "python sm3_signature.py \"message\"")
        message = input("请输入你的原始消息：").encode('utf-8')
        secret_key = input("请输入你的密钥：").encode('utf-8')
        #result = sm3(message)
        #print(result)
        print("签名后的数据流：\n" + signature(message,secret_key))



