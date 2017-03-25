#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import binascii
import math
import sys
import wave
import pulseaudio as pa
import numpy as np
import coding as D

def send_data(x, time, zero, one):
    zero_x = 44100/(math.pi * 2 * zero)
    one_x = 44100/(math.pi * 2 * one)
    zero_frames = [math.sin(i/zero_x)*24000 for i in range(int(44100*time))]
    one_frames = [math.sin(i/one_x)*24000 for i in range(int(44100*time))]
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
        for c in x:
            if c == '0':
                player.write(zero_frames)
            else:
                player.write(one_frames)
        player.drain()

time = float(1/float(sys.argv[1]))
zero = float(sys.argv[2])
one = float(sys.argv[3])
for lines in sys.stdin:
    send_data(D.encoding(lines), time, zero, one)
