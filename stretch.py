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
        bufsize = int(float(bufsize) * float(indatalen)) / 100
    except:
        print("stretch: error calculating bufsize")
    try:
        max = infs * 60 * float(max)
        print("MAX:", max)
    except:
        print("stretch: couldn't calculate max")
    try:
        offset = int(float(offset) * 1000)
        if offset > bufsize and bufsize > 0:
            offset = offset % bufsize
            print("offset % bufsize")
        if offset > abs(end - start):
            offset = offset % abs(end - start)
            print("offset % end - start")
        if offset > max:
            offset = offset % max
            print("offset % max")
        else:
            offset = offset
    except:
        print("stretch:couldn't calculate offset")

    # create temp buffers
    temp = []

    print("processing...")
    # main loop
    try:
        # with loop buffer
        if bufsize > 0:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    for k in range(int(bufsize)):
                        if i + k < int(end):
                            try:
                                temp.append(indata[i + k])
                            except:
                                print(i, k, (i+k))
                                print("stretch:error: can't append?")
                            else:
                                temp.append(indata[i])
                            if i + int(offset) < int(end):
                                i = i + int(offset)
                            else:
                                i = int(offset) - i
                    # break from loop when max reached
                    # there should be a better way to do this...
                    if len(temp) >= max:
                        i = int(end)
                        k = int(bufsize)
                        j = int(factor)
                        # print(f"i {i}. j {j}. k {k} max {max}. int(end) {int(end)}, len(temp {len(temp)})")
                        # print("reached max!")
                        break
                if len(temp) >= max:
                    i = int(end)
                    k = int(bufsize)
                    j = int(factor)
                    # print(f"i {i}. j {j}. k {k} max {max}. int(end) {int(end)}, len(temp {len(temp)})")
                    # print("reached max!")
                    break
        # no loop buffer
        else:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    temp.append(indata[i])
                    if i + int(offset) < int(end):
                        i = i + int(offset)
                    else:
                        break
                # break when max reached
                if len(temp) >= max:
                    i = int(end)
                    j = int(factor)
                    # print("lentemp after max reached", len(temp))
                    # print("reached max!")
                    break

        print("stretch: done processing")
    except ValueError:
        print("stretch: couldn't iterate")
        raise ValueError()

    # write to numpy array
    processed = []
    try:
        processed = (np.asarray(temp, dtype="int16"))
    except:
        print("stretch: couldn't write buffer to numpy")
    print(f"{len(processed)} samples processed")
    # print(type(processed))
    return (processed, infs)

    # close and del buffers
    try:
        sf.SoundFile(infile).close()
        del temp[:]
        del processed[:]
    except:
        print("couldn't close/del buffers")
