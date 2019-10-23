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
        pass # print("stretch: error calculating startpoint")
    try:
        end = (float(end_input) * float(indatalen)) / 100
    except ValueError:
        pass# pass # print("stretch: error calculating endpoint")
    try:
        bufsize = int(float(bufsize) * (end - start)) / 100
        pass # print("bufsize", bufsize)
        # bufsize = int(float(bufsize) * float(end - start))/20
    except:
        pass # print("stretch: error calculating bufsize")
    try:
        max = infs * 60 * float(max)
        pass # print("MAX:", max)
    except:
        pass # print("stretch: couldn't calculate max")
    try:
        offset = int(float(offset) * 10000)
        if offset > bufsize and bufsize > 0:
            offset = offset % bufsize
            pass # print("offset % bufsize")
        if offset > abs(end - start):
            offset = offset % abs(end - start)
            pass # print("offset % end - start")
        if offset > max:
            offset = offset % max
            pass # print("offset % max")
        else:
            offset = offset
            pass # print("offset=offset")
    except:
        pass # print("stretch:couldn't calculate offset")

    # create temp buffers
    temp = []

    pass # print("processing...")
    # main loop
    negfact = 0
    try:
        if factor == 0:
            factor = 1
        if factor < 0:
            factor = abs(factor)
            negfact = 1

        # with loop buffer
        if bufsize > 0:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    for k in range(int(bufsize)):
                        if i + k < int(end):
                            if k > 10:
                                try:
                                    temp.append(indata[i + k])
                                except:
                                    pass # print(i, k, (i+k))
                                    pass # print("stretch:error: can't append?")
                            elif len(temp) > 0:
                                # pass # print(len(temp))
                                a = temp[-1]
                                # pass # print(a)
                                b = indata[i + k]
                                temp.append((a+b)/2)
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

        pass # print("stretch: done processing")
    except ValueError:
        pass # print("stretch: couldn't iterate")
        raise ValueError()

    # write to numpy array
    processed = []
    try:
        processed = (np.asarray(temp, dtype="int16"))
    except:
        pass # print("stretch: couldn't write buffer to numpy")
    pass # print(f"{len(processed)} samples processed")
    # pass # print(type(processed))
    return (processed, infs)

    # close and del buffers
    try:
        sf.SoundFile(infile).close()
        del temp[:]
        del processed[:]
    except:
        pass # print("couldn't close/del buffers")
