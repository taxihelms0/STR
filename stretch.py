# stretch 2019
# alex ian smith

# from tkinter import *
from scipy.io.wavfile import write
import scipy.io.wavfile
import os.path
# import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
# import wave
import time
import struct
import numpy as np
import sys



def stretch0(indata, infs, factor, bufsize, offset, start_input, end_input,
max):

    indatalen = len(indata)

    # calculate parameters
    try:
        start = int((start_input * indatalen) / 100)
    except ValueError:
        print("stretch: error calculating startpoint")
    try:
        end = (float(end_input) * float(indatalen)) / 100
    except ValueError:
        print("stretch: error calculating endpoint")
    try:
        bufsize = int(float(bufsize) * (end - start)) / 100
        print("bufsize", bufsize)
        # bufsize = int(float(bufsize) * float(end - start))/20
    except:
        print("stretch: error calculating bufsize")
    try:
        max = infs * 60 * float(max)
        print("MAX:", max)
    except:
        print("stretch: couldn't calculate max")
    try:
        offset = int(float(offset) * 10000)
        if offset > bufsize and bufsize > 0:
            offset = offset % bufsize
            # print(offset)
            print("offset % bufsize")
        if offset > abs(end - start):
            offset = offset % abs(end - start)
            # print(offset)
            print("offset % end - start")
        if offset > max:
            offset = offset % max
            # print(offset)
            print("offset % max")
        else:
            offset = offset
            # print(offset)
            print("offset=offset")
    except:
        print("stretch:couldn't calculate offset")

    if bufsize > max:
        try:
            bufsize = (bufsize % max)
            print("bufsize looped w/ modulo")
        except:
            print("bufsize too big?")


    # create temp buffers
    temp = []

    print("processing...")
    # main loop
    negfact = 0
    smoothbuf = int(bufsize/128)
    try:
        if factor == 0:
            factor = 1
        if factor < 0:
            factor = abs(factor)
            negfact = 1 # Negative Factor Flag

        # with loop buffer
        if bufsize > 0:
            for i in range(int(start), int(end)):

                for j in range(int(factor)):

                    for k in range(int(bufsize)):

                        if i + k < int(end):
                            if k > smoothbuf:
                                try:
                                    temp.append(indata[i + k])
                                except:
                                    print(i, k, (i+k))
                                    print("stretch:error appending indata[i+k]")
                            elif len(temp) > 0:
                                # pass # print(len(temp))
                                try:
                                    z = (1 + k)
                                except:
                                    print("couldn't calculate z")
                                a = temp[-1] # previously written sample
                                # pass # print(a)
                                try:
                                    b = indata[i + k]
                                except:
                                    print("couldn't calculate b")
                                try:
                                    c = ((a-b)/smoothbuf)
                                except:
                                    print("couldn't calculate c")
                                d = (smoothbuf - z)
                                try:
                                    temp.append(c * d + b)
                                    # print(f"{a} + {b} /2 + {c} =", int(a+b)/2 + c)
                                except:
                                    print("error appending smooth buffer")

                        # else:
                        #     temp.append(indata[i])
                        if negfact == 1:
                            if i + int(offset) < int(end):
                                i = i + int(offset)
                            else:
                                i = int(offset) - i
                    if negfact == 0:
                        if i + int(offset) < int(end):
                            i = i + int(offset)
                        else:
                            i = int(offset) - i

                    if len(temp) >= max:
                        i = int(end)
                        k = int(bufsize)
                        j = int(factor)
                        # pass # print(f"i {i}. j {j}. k {k} max {max}. int(end) {int(end)}, len(temp {len(temp)})")
                        # pass # print("reached max!")
                        break
                if len(temp) >= max:
                    i = int(end)
                    k = int(bufsize)
                    j = int(factor)
                    # pass # print(f"i {i}. j {j}. k {k} max {max}. int(end) {int(end)}, len(temp {len(temp)})")
                    # pass # print("reached max!")
                    break
        # no loop buffer
        else:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    temp.append(indata[i])
                    if negfact == 1:
                        if i + int(offset) < int(end):
                            i = i + int(offset)
                        else:
                            break
                if negfact == 0:
                    if i + int(offset) < int(end):
                        i = i + int(offset)
                    else:
                        i = int(offset) - i
                # break when max reached
                if len(temp) >= max:
                    i = int(end)
                    j = int(factor)
                    # pass # print("lentemp after max reached", len(temp))
                    # pass # print("reached max!")
                    break

        print("stretch: done processing")
    except:
        print("stretch: couldn't iterate")

        # raise ValueError()
        # print(ValueError())
        # pass

    # write to numpy array
    processed = []
    try:
        print("writing to 'processed'")
        processed = (np.asarray(temp, dtype="int16"))
    except:
        print("couldn't write array")
        pass
    # print("stretch: couldn't write buffer to numpy")
    print(f"{len(processed)} samples processed")
    # pass # print(type(processed))
    return (processed, infs)

    # close and del buffers
    try:
        sf.SoundFile(infile).close()
        del temp[:]
        del processed[:]
    except:
        pass # print("couldn't close/del buffers")
