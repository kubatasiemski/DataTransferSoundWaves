#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import pulseaudio as pa
import numpy as np
import coding as D

def frequency(time, recorder):
    nframes = int(float(time)*recorder.rate)
    a = recorder.read(nframes)
    b = np.fft.fft(a)
    a_nf = int(float(time)*recorder.rate)
    result = (np.argmax(np.abs(b[0:a_nf/2]))/float(time))
    return result

def adaptation(time, recorder):
    x = frequency(time/25, recorder)
    a = recorder.read(int(float(time*23/25)*recorder.rate))
    y = frequency(time/25, recorder)
    if (x == y):
        return 1
    return 0

time = float(1/float(sys.argv[1]))
zero = float(sys.argv[2])
one = float(sys.argv[3])
with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as recorder:  
    while True:
        i = 0
        try:
            while True:
                x = frequency(time, recorder)
                if x == 0.0:
                    i = 0
                elif np.abs(1-float(one/x)) < 0.25:
                    i += 1
                elif np.abs(1-float(zero/x)) < 0.25:
                    i += 1
                else:
                    i = 0
                if i == 5:
                    break
        except Exception as e:
            break

        for j in range(40):
            x = adaptation(time, recorder)
            if x == 1:
                break
            recorder.read(int(float(time/25)*recorder.rate))
    
        y = 0.0
        while True:
            x = frequency(time, recorder)
            if x == y:
                break
            y = x

        result = "D " + str(D.preamble())
        while True:
            try:
                x = frequency(time, recorder)
            except Exception as e:
                break
            if x == 0.0:
                break
            if x == zero:
                result += '0'
            elif x == one:
                result += '1'
            elif np.abs(1-float(one/x)) < 0.25:
                result += '1'
            elif np.abs(1-float(zero/x)) < 0.25:
                result += '0'
            else:
                break
        excess = (len(result[2:])-64) % 5
        if excess > 0:
            result = result[:-excess]
        try:
            D.coding(result)
        except Exception as e:
            pass
