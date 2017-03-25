import binascii
import sys
import pulseaudio as pa
import numpy as np

coding_table = {
    '0000':'11110',
    '0001':'01001',
    '0010':'10100',
    '0011':'10101',
    '0100':'01010',
    '0101':'01011',
    '0110':'01110',
    '0111':'01111',
    '1000':'10010',
    '1001':'10011',
    '1010':'10110',
    '1011':'10111',
    '1100':'11010',
    '1101':'11011',
    '1110':'11100',
    '1111':'11101'
}

decoding_table = {
    '11110':'0000',
    '01001':'0001',
    '10100':'0010',
    '10101':'0011',
    '01010':'0100',
    '01011':'0101',
    '01110':'0110',
    '01111':'0111',
    '10010':'1000',
    '10011':'1001',
    '10110':'1010',
    '10111':'1011',
    '11010':'1100',
    '11011':'1101',
    '11100':'1110',
    '11101':'1111'
}

def preamble():
    x = ""
    for i in range(7): x += "10101010"
    x += "10101011"
    return x

def nrz(x):
    if x[:1] == '1':
        res = '0'
    else:
        res = '1'
    last = x[:1]
    for c in x[1:]:
        if last == c:
            res += '0'
        else:
            last = c
            res += '1'
    return res

def nrz_e(x):
    if x[:1] == '1':
        res = '0'
    else:
        res = '1'
    last = res
    for c in x[1:]:
        if c == '1':
            if last == '1':
                last = '0'
            else:
                last = '1'
        res += last
    return res


def b4b5(x, n):
    b4b5table = coding_table
    res = ""
    if n == 5:
        b4b5table = decoding_table
    for i in range(0, len(x), n):
        res += b4b5table[x[i:i+n]]
    return res

def bit_to_num(x):
    res = 0
    two = 1
    i = len(x)-1
    while (i > -1):
        if (x[i:i+1] == '1'):
            res += two
        two *= 2
        i -= 1
    return res

def becomplete(x):
    brak = 8 - len(x)
    for i in range (brak): x = '0' + x
    return x

def message(x):
    res = ''
    b = x.encode('utf-8')
    data = bytearray(b)
    for value in data:
        res = res + becomplete("{0:b}".format(int(value)))
    return res

def adress(x):
    res = "{0:b}".format(int(x))
    b = 6*8-len(res)
    for i in range (b):
        res = "0" + res
    return res

def mylen(x):
    res = "{0:b}".format(int(x))
    b = 2*8-len(res)
    for i in range(b):
        res = "0" + res
    return res

def getcrc(x):
    l = int(len(x)/8)
    w = bytearray()
    for i in range(l):
        w.append(int(x[(i) * 8:(i+1) * 8], 2))
    crc = (binascii.crc32(w))
    crc = crc & 0xffffffff
    crcfromx = '%08x' % crc
    bits = ""
    for x in range(0, len(crcfromx), 2):
        k = int(crcfromx[x:x + 2], 16)
        k = "{0:b}".format(int(k))
        k = becomplete(k)
        bits += k
    return bits

def crc32(x, l):
    w = bytearray()
    for i in range (4):
        w.append(int(x[(14+l+i)*8:(15+l+i)*8], 2))
    x = x[:-4*8]
    k = bytearray()
    for i in range(14+l):
        k.append(int(x[i*8:(i+1)* 8], 2))
    crc = (binascii.crc32(k)) & 0xffffffff
    crcfromx = '%08x' % crc
    crcdane = "".join(map(lambda b: format(b, "02x"), w))
    if crcfromx == crcdane:
        return 1
    else:
        return 0

def encoding(x):
    c = x.split(' ', 2)
    w = message(c[2])
    l = mylen(len(c[2]))
    n = adress(c[0])
    o = adress(c[1])
    c = getcrc(o+n+l+w)
    try:
        res = nrz_e(b4b5(o+n+l+w+c, 4))
        return preamble() + res
    except Exception as e:
        return ""

def decoding(x):
    res = ""
    if (x[:64] == preamble()):
        x = nrz(x[64:])
        try:
            x = b4b5(x, 5)
        except Exception as e:
            return res
        if len(x) > 18*8-1:
            k = bytearray()
            k.append(int(x[12*8:14*8], 2))
            l = k[0]
            if (len(x) == (18+l)*8):
                crc = crc32(x, l)
                if crc == 1:
                    w = bytearray()
                    res = str(bit_to_num(x[6*8:12*8])) + " "
                    res += str(bit_to_num(x[:6*8])) + " "
                    for i in range(l):
                        w.append(int(x[(14+i)*8:(15+i) * 8], 2))
                    res += w.decode('utf-8')
    return res

def coding(lines):
    if (len(lines) > 0):
        if (lines[-1:] == '\n'):
            lines = lines[:-1]
        if lines[:1] == 'E':
            print(encoding(lines[2:]))
        elif lines[:1] == 'D':
            print(decoding(lines[2:]))
