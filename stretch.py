# STR Version 0.1.0
# © Alex Ian Smith 2019
#
# License Notice:
# This file is part of STR.
#
# STR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STR.  If not, see <https://www.gnu.org/licenses/>.

# Stretch Function for processing wav files.

import time
import numpy as np
import sys


def stretch0(indata, infs, factor, bufsize, offset, start_input, end_input,
max):
    # actual stretch function that does the processing
    start = start_input
    end = end_input
    # define indatalen for calculations
    indatalen = len(indata)

    # calculate parameters
    # start

####################################################
    try:
        start = int((start_input * indatalen) / 100)
    except:
        print("stretch: error calculating startpoint")
    # end
    try:
        end = (float(end_input) * float(indatalen)) / 100
    except ValueError:
        print("stretch: error calculating endpoint")
    # bufsize
    try:
        bufsize = int(float(bufsize) * (end - start)) / 100
        print("bufsize", bufsize)
    except:
        print("stretch: error calculating bufsize")
    # max
    try:
        max = infs * 60 * float(max)
        print("MAX:", max)
    except:
        print("stretch: couldn't calculate max")
    # offset
    try:
        offset = int(float(offset) * 10000)
        # offset scaling
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
            print("offset=offset")
    except:
        print("stretch:couldn't calculate offset")

    # scale bufsize
    if bufsize > max:
        try:
            bufsize = (bufsize % max)
            print("bufsize looped w/ modulo")
        except:
            print("bufsize too big?")
################################################

    # create temp buffers and adjust values
    temp = []
    negfact = 0
    smoothbuf = int(bufsize/32)
    if smoothbuf == 0:
        smoothbuf = 1
    if smoothbuf < 1 and bufsize == 0:
        smoothbuf = 10
        bufsize = 1
    # try:
    if 1 == 1:
        if factor == 0:
            factor = 1
        if factor < 0:
            factor = abs(factor)
            negfact = 1 # Negative Factor Flag

        # main processing loop begins here
        # process with loop buffer
        if bufsize > 0:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    for k in range(int(bufsize)):
                        if i + k < int(end):
                            if k > smoothbuf:
                                try:
                                    temp.append(indata[i + k])
                                except:
                                    break
                                    # print(i, k, (i+k))
                                    # print("stretch:error appending indata[i+k]")
                            elif len(temp) > 0:
                                try:
                                    z = (1 + k)
                                except:
                                    print("couldn't calculate z")
                                a = temp[-1] # previously written sample
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
                                except:
                                    print("error appending smooth buffer")
                        # apply 'negative' i iteration
                        if negfact == 1:
                            if i + int(offset) < int(end):
                                i = i + int(offset)
                            else:
                                i = int(offset) - i
                    # apply 'non-negative' i iteration
                    if negfact == 0:
                        if i + int(offset) < int(end):
                            i = i + int(offset)
                        else:
                            i = int(offset) - i
                    # stop processing at max
                    if len(temp) >= max:
                        break
                # stop processing at max length
                if len(temp) >= max:
                    break

        # Alternate processing loop with no loop buffer
        else:
            for i in range(int(start), int(end)):
                for j in range(int(factor)):
                    temp.append(indata[i])
                    # 'negative' iteration
                    if negfact == 1:
                        if i + int(offset) < int(end):
                            i = i + int(offset)
                        else:
                            break
                # non-negative iteration
                if negfact == 0:
                    if i + int(offset) < int(end):
                        i = i + int(offset)
                    else:
                        i = int(offset) - i
                # stop processing when max reached
                if len(temp) >= max:
                    break
    # except:
    #     print("stretch: couldn't iterate")

    # write processed data to numpy array
    processed = []
    try:
        processed = (np.asarray(temp, dtype="int16"))
    except:
        print("couldn't write array")
        pass
    print(f"{len(processed)} samples processed")
    return (processed, infs)

    # close and del buffers
    try:
        sf.SoundFile(infile).close()
        del temp[:]
        del processed[:]
    except:
        pass
