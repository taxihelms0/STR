
 ______________     ________________    _______________
________________    ________________    ________________
______    ______    ________________    ______    ______
______                   ______         ______    ______
 ______________          ______         _______________
          ______         ______         _______________   
______    ______         ______         ______    ______     
________________         ______         ______    ______    
 ______________          ______         ______    ______   
                   

STR is an application for MacOs. It's function is the
manipulation of .wav files by altering elements in the
time domain.

* Disclaimer *
  As it is software that processes audio, the output from
  STR can at times be extremely loud. At other times it
  can be extremely quiet. Please take care when setting
  your computer volume while Previewing or Playing your
  results, especially while wearing headphones. Speaker
  and/or hearing damage are possible. Please use your own
  discretion.

The controls are loosely named by not only how they affect
the results, but also as they function within STR's
algorithms. All the controls in some way affect the time
domain and may change in response depending on how you set
the rest of the sliders. So, they might not always do what
you expect. Don't read into that too much.

Slider Functions(sometimes):

Factor:
    Factor by which the original is slowed down
Buffer:
    Loops a section of the file in relation to the
    selected factor
Offset:
    Amount to offset the buffer on each successive
    loop
Start:
    Point in the original file to start reading
End:
    Point in the original file to stop reading
    * STR currently won't work if you make Start
      larger than End. I hope to fix this in a
      future update.
Max Length:
    The longest your results will be. Longer Max
    Length will result in longer processing times.
    * For times longer than a couple minutes, expect
      to let STR run for about 1-2 minutes. For Max
      Lengths of 30 minutes to 59 minutes, STR could
      run for 20+ minutes to process the results.
      Your computer will probably start to heat up
      and don't be alarmed when its fan turns on.
      You've been warned.

Button Functions:

Open:
    Launch a file open dialog to select a .wav file
Play:
    Listen to your loaded .wav file before processing
Random:
    Randomize the slider positions
Process:
    Run the loaded wav file through STR's algorithms
Preview:
    Listen to the results of the processing
Save:
    Save those results to a new .wav file
    * If you click process again or close the window
      your results won't be saved. If you are happy with
      the results, remember to save!
About:
    Opens the 'About' window

* Important to note *
STR is not designed for real-time audio manipulation. This means that you can't

STR handles both Stereo and Mono .wav files as well as
various samplerates. It processes wav files at 16 Bits
per sample.

STR was written with Python and utilizes both the soundfile
and sounddevice modules for working with .wav files.
    https://pypi.org/project/SoundFile/
    https://python-sounddevice.readthedocs.io/en/0.3.14/#
STR's graphical user interface was programmed using PyQt.
    https://pypi.org/project/PyQt5/

Please send any comments, bugs, or feature suggestions to
alexander.ian.smith@gmail.com

© Alex Ian Smith 2019
alexiansmith.com
