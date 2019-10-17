# STR Version 0.1.0
# © Alex Ian Smith 2019

import sys
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget,
QInputDialog, QLineEdit, QFileDialog, QSlider, QDialog, QVBoxLayout, QLabel,
QGridLayout, QStatusBar, QToolButton, QHBoxLayout, QStyleFactory, QMainWindow,
QProgressBar)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread, pyqtSignal
import math
import random
from pathlib import Path
import sounddevice as sd
import soundfile as sf
import threading
import os
import ntpath
from stretch import stretch0
from scipy.io.wavfile import write
import numpy
import webbrowser
import time

# future stuff:
# 1. create dicts for buttons/frames, etc, so all you have to do is iterate
# through the list to load everything (less copy/paste)
#
# 2. create one layout template that gets reused, but changes the names/values of
# buttons based on which tab is clicked

class Process_function(QThread):
    stretch_results = pyqtSignal(numpy.ndarray, int)
    #processes the things
    def doit(self, data, fs, factor_value, buffer_value, offset_value,
    start_value, end_value, max_value):
        app.processEvents()
        write_data, write_fs = stretch0(data, fs,
        factor_value, buffer_value, offset_value,
        start_value, end_value, max_value)

        # App().onButtonClick(f"{len(write_data)} samples at {fs}")
        self.stretch_results.emit(write_data, write_fs)

class External(QThread):
    """
    Runs a counter thread.
    """
    messageChanged = pyqtSignal(str)

    def status(self, message):
        self.messageChanged.emit(message)

class App(QWidget):

    def onButtonClick(self, message):
        # print(message)
        self.calc = External()
        self.calc.messageChanged.connect(self.onMessageChanged)
        self.calc.status(message)

    def onMessageChanged(self, message):
        self.statuslabel.setText(message)

    def processClick(self):
        app.processEvents()
        self.update()

        self.click = Process_function()
        self.click.stretch_results.connect(self.recieveResults)
        self.click.doit(self.data, self.fs, self.factor_value,
        self.buffer_value, self.offset_value, self.start_value, self.end_value,
        self.max_value)

    def recieveResults(self, data, fs):
        self.onButtonClick('')
        self.write_data = data
        self.write_fs = fs

    def __init__(self):
        super().__init__()
        self.title = 'STR'
        self.left = 200
        self.top = 200
        self.width = 800
        self.height = 200
        self.colwidth = 110
        self.initbuttons()
        self.initsliders()
        self.initUI()
        self.initval()
        self.update()

    def initval(self):
        # stretch0(self.data, self.fs, self.factor_value, self.buffer_value,
        # self.offset_value, self.start_value, self.end_value, self.max_value)
        self.data = 0
        self.fs = 0
        self.factor_value = 1
        self.buffer_value = 0
        self.offset_value = 0
        self.start_value = 0
        self.end_value = 99
        self.max_value = 0.0165
        self.filename = 0

    # def initstatus(self):
    #     self.statusBar = QStatusBar()
    #     self.setStatusBar(self.statusBar)
    #     self.statusbar().showMessage("Statusbar")

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.setWindowIcon(QIcon('sine.png'))
        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        # self.setStyleSheet("QLabel, QPushButton {font: 14pt Courier}")

        self.filelabel = QLabel("\n\n")
        self.layout.addWidget(self.filelabel, 11, 0, 2, 2)
        self.layout.addWidget(self.openbutton, 12, 2)
        self.layout.addWidget(self.playbutton, 12, 3)
        self.layout.addWidget(self.randombutton, 12, 6)
        self.layout.addWidget(self.processbutton, 12, 7)
        self.layout.addWidget(self.previewbutton, 12, 8)
        self.layout.addWidget(self.savebutton, 12, 10)
        self.layout.addWidget(self.aboutbutton, 12, 11)

        self.layout.addWidget(self.factorlabel, 0, 0, 1, 2)
        self.layout.addWidget(self.factorslider, 0, 2, 1, 10)
        self.layout.addWidget(self.buflabel, 2, 0)
        self.layout.addWidget(self.bufslider, 2, 2, 1, 10)
        self.layout.addWidget(self.offsetlabel, 4, 0)
        self.layout.addWidget(self.offsetslider, 4, 2, 1, 10)
        self.layout.addWidget(self.startlabel, 6, 0)
        self.layout.addWidget(self.startslider, 6, 2, 1, 10)
        self.layout.addWidget(self.endlabel, 8, 0)
        self.layout.addWidget(self.endslider, 8, 2, 1, 10)
        self.layout.addWidget(self.maxlabel, 10, 0)
        self.layout.addWidget(self.maxslidermin, 10, 2, 1, 10)
        self.layout.addWidget(self.maxslidersec, 11, 2, 1, 10)

        self.statuslabel = QLabel('')
        self.layout.addWidget(self.statuslabel, 13, 2, 1, 10)

        self.setLayout(self.layout)
        self.update()

        self.show()

    def initbuttons(self):
        # buttons
        # open
        self.openbutton = QPushButton("Open", self)
        self.openbutton.setToolTip('Open a Wav file')
        self.openbutton.clicked.connect(self.openFileNameDialog)

        # play
        self.playbutton = QPushButton("Play", self)
        # self.playbutton.setText('Play')
        # self.playbutton.setChecked(False)
        self.playbutton.setToolTip('play selected .wav file')
        self.playbutton.clicked.connect(self.play)

        # random
        self.randombutton = QPushButton("Random", self)
        self.randombutton.setToolTip('Randomize settings')
        self.randombutton.clicked.connect(self.randomize)

        # process
        self.processbutton = QPushButton("Process", self)
        self.processbutton.setToolTip('Processes Wav file')
        self.processbutton.clicked.connect(self.process)

        # preview
        self.previewbutton = QPushButton("Preview", self)
        self.previewbutton.setToolTip('Preview Processed Results')
        self.previewbutton.clicked.connect(self.preview)

        # save
        self.savebutton = QPushButton("Save", self)
        self.savebutton.setToolTip('Saves to a new Wav file')
        self.savebutton.clicked.connect(self.saveFileDialog)

        # about
        self.aboutbutton = QPushButton("About", self)
        self.aboutbutton.clicked.connect(self.aboutdialog)

    def initsliders(self):
        # Sliders
        # factor
        self.factorslider = QSlider(Qt.Horizontal)
        self.factorslider.setMinimum(1)
        self.factorslider.setMaximum(100)
        self.factorslider.setValue(1)
        self.factorslider.valueChanged.connect(self.factor)
        self.factorlabel = QLabel('Factor:\n1')
        self.factorlabel.setFixedWidth(self.colwidth)
        self.factorlabel.setAlignment(Qt.AlignRight)

        # buffer
        self.bufslider = QSlider(Qt.Horizontal)
        self.bufslider.setMinimum(0)
        self.bufslider.setMaximum(59999)
        self.bufslider.setValue(0)
        self.bufslider.setSingleStep(1)
        self.bufslider.valueChanged.connect(self.buf)
        self.buflabel = QLabel('Buffer:\n0.0')
        self.buflabel.setFixedWidth(self.colwidth)
        self.buflabel.setAlignment(Qt.AlignRight)

        # offset
        self.offsetslider = QSlider(Qt.Horizontal)
        self.offsetslider.setMinimum(0)
        self.offsetslider.setMaximum(1000)
        self.offsetslider.setValue(0)
        self.offsetslider.setSingleStep(1)
        self.offsetslider.valueChanged.connect(self.offset)
        self.offsetlabel = QLabel('Offset:\n0.0')
        self.offsetlabel.setFixedWidth(self.colwidth)
        self.offsetlabel.setAlignment(Qt.AlignRight)

        # startpoint
        self.startslider = QSlider(Qt.Horizontal)
        self.startslider.setMinimum(0)
        self.startslider.setMaximum(99)
        self.startslider.setValue(0)
        self.startslider.setSingleStep(1)
        self.startslider.valueChanged.connect(self.start)
        self.startlabel = QLabel('Start:\n0')
        self.startlabel.setFixedWidth(self.colwidth)
        self.startlabel.setAlignment(Qt.AlignRight)

        # endpoint
        self.endslider = QSlider(Qt.Horizontal)
        self.endslider.setMinimum(0)
        self.endslider.setMaximum(99)
        self.endslider.setValue(99)
        self.endslider.setSingleStep(1)
        self.endslider.valueChanged.connect(self.end)
        self.endlabel = QLabel('End:\n99')
        self.endlabel.setFixedWidth(self.colwidth)
        self.endlabel.setAlignment(Qt.AlignRight)

        # max size
        self.maxslidermin = QSlider(Qt.Horizontal)
        self.maxslidermin.setMinimum(0)
        self.maxslidermin.setMaximum(59)
        self.maxslidermin.setValue(0)
        self.maxslidermin.setSingleStep(1)
        self.maxslidermin.valueChanged.connect(self.max)
        self.maxslidersec = QSlider(Qt.Horizontal)
        self.maxslidersec.setMinimum(0)
        self.maxslidersec.setMaximum(5999)
        self.maxslidersec.setValue(99)
        self.maxslidersec.setSingleStep(1)
        self.maxslidersec.valueChanged.connect(self.max)
        self.maxlabel = QLabel('Max Length:\n0 min 0.99 sec')
        self.maxlabel.setFixedWidth(self.colwidth)
        self.maxlabel.setAlignment(Qt.AlignRight)

    def open_webbrowser(self):
        webbrowser.open('http://alexiansmith.com')

    def factor(self):
        self.update()
        self.factor_value = self.factorslider.value()
        self.factorlabel.setText('Factor:\n' + str(self.factor_value))

    def buf(self):
        self.update()
        self.buffer_value = float(self.bufslider.value()/1000)
        self.buflabel.setText('Buffer:\n' + str(self.buffer_value))

    def offset(self):
        self.offset_value = float(self.offsetslider.value()/1000)
        self.offsetlabel.setText('Offset:\n' + str(self.offset_value))

    def start(self):
        self.start_value = self.startslider.value()
        self.startlabel.setText('Start:\n' + str(self.start_value))

    def end(self):
        self.end_value = self.endslider.value()
        self.endlabel.setText('End:\n' + str(self.end_value))

    def max(self):
        min = int(self.maxslidermin.value())
        sec = float((self.maxslidersec.value())/100)
        self.max_value = (min + sec/60)
        # print(self.max_value)
        self.maxlabel.setText(f'Max Length:\n{str(min)} min {str(sec)} sec')
        if self.max_value > 1.5:
            self.onButtonClick("Careful! more than a couple minutes can take A LOT of time and computer resources to process")
        else:
            self.onButtonClick('')

    def open(self):
        try:
            self.data, self.fs = sf.read(self.filename, dtype='int16')
            self.filelabel.setText("File Loaded:\n" + ntpath.basename(self.filename))
            self.filelabel.setAlignment(Qt.AlignRight)
        except:
            self.onButtonClick("Couldn't load wav file")

    def play(self):
        # print(self.playbutton.isChecked())

        if self.filename != 0:
            if self.playbutton.text() == 'Stop':
                try:
                    self.onButtonClick('')
                    self.timer.cancel()
                except:
                    print("couldn't stop timer")
                self.playbutton.setText('Play')
                sd.stop()
                # self.playbutton.toggle()
            else:
                try:
                    self.onButtonClick('Playing...')
                    l = (len(self.data) / self.fs)
                    # print(f"{l} seconds")
                    sd.play(self.data, self.fs)
                    self.playbutton.setText('Stop')
                    self.timer = threading.Timer(l, self.revert_playbutton)
                    self.timer.start()
                except:
                    self.onButtonClick("couldn't play")

        else:
            self.onButtonClick("Nothing to play. Open a file first")

    def revert_playbutton(self):
        self.onButtonClick('')
        self.playbutton.setText('Play')

    def randomize(self):
        self.update()
        self.f = random.uniform(1, 20)
        self.b = random.uniform(0, 99000)
        self.o = random.uniform(0, 1000)
        self.s = random.uniform(0, 60)
        self.e = random.uniform(0, 99)
        self.update()
        self.factorslider.setValue(self.f)
        self.bufslider.setValue(self.b)
        self.offsetslider.setValue(self.o)
        self.startslider.setValue(self.s)
        self.e = random.uniform(self.startslider.value(), 99)
        self.endslider.setValue(self.e)
        self.update()

    def preview(self):

        if self.previewbutton.text() == 'Stop':
            try:
                self.onButtonClick('')
                self.ptimer.cancel()
            except:
                print("couldn't stop timer")
            self.previewbutton.setText('Preview')
            sd.stop()
            # self.playbutton.toggle()
        else:
            try:
                self.onButtonClick('Previewing...')
                l = (len(self.write_data) / self.write_fs)
                # print(f"{l} seconds")
                sd.play(self.write_data, self.write_fs)
                self.previewbutton.setText('Stop')
                self.ptimer = threading.Timer(l, self.revert_previewbutton)
                self.ptimer.start()
            except:
                self.onButtonClick("Nothing to preview. Process something first")

    def revert_previewbutton(self):
        self.onButtonClick('')
        self.previewbutton.setText('Preview')

        # try:
        #     sd.play(self.write_data, self.write_fs)
        # except:
        #     print("couldn't preview")

    def process(self):
        if self.start_value > self.end_value:
            # temp = []
            # indatalen = len(self.data)
            # for i in range(indatalen):
            #     temp.append(self.data[indatalen - i - 1])
            # newstart = 99 - self.start_value
            # newend = 99 - self.end_value
            # print(f"newend {newend}, newstart {newstart}")
            # start_value = newstart
            # end_value = newend
            self.onButtonClick("Startpoint cannot be larger than Endpoint")
        else:

            self.onButtonClick("Processing...   STR will be unresponsive until Process completes")
            self.processClick()
            self.update()




    def revert_processing(self):
        self.onButtonClick('')

    def save(self):
        try:
            # save write_buffer to file
            write(self.save_filename, self.write_fs, self.write_data)
            self.onButtonClick(f"{ntpath.basename(self.save_filename)} saved")
        except:
            self.onButtonClick(f"save error: couldn't save {ntpath.basename(self.save_filename)}")

    def openFileNameDialog(self):
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # file = inspect.getframeinfo(inspect.currentframe()).filename

        home = str(Path.home())
        # base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","",home,"Wav Files (*.wav)")
        if self.filename:
            print(self.filename)
            self.open()

    def ReadMe(self):
        os.system('open ReadMe.md')

    def aboutdialog(self):
        self.aboutwindow = QDialog()
        # self.aboutwindow.setGeometry(self.left + 50, self.top + 50, 400, 300)

        b1 = QPushButton("alexiansmith.com",self.aboutwindow)
        b1.clicked.connect(self.open_webbrowser)
        b2 = QPushButton("Close")
        b2.clicked.connect(self.aboutwindow.close)
        b3 = QPushButton("ReadMe")
        b3.clicked.connect(self.ReadMe)
        l1 = QLabel("STR is an application for manipulating '.wav' files\nfor creative and sometimes unexpected results\n\n © Alex Ian Smith 2019\n\n")

        abt = QVBoxLayout()
        abt.addWidget(l1)
        abt.addStretch()
        abt.addWidget(b3)
        abt.addWidget(b1)
        abt.addWidget(b2)
        self.aboutwindow.setLayout(abt)
        self.aboutwindow.setWindowTitle("About")
        self.aboutwindow.setWindowModality(Qt.ApplicationModal)
        self.aboutwindow.exec_()

    def saveFileDialog(self):
        try:
            if self.write_fs:
                # options = QFileDialog.Options()
                # options |= QFileDialog.DontUseNativeDialog
                home = str(Path.home())
                self.save_filename, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","",home,"Wav Files (*.wav)")
                if self.save_filename:
                    print(self.save_filename)
                    self.save()
        except:
            self.onButtonClick("Nothing to save. Process something first")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.setWindowIcon(QIcon(base_dir + '/STR-icon.png'))
    ex = App()

    app.setStyle('Fusion')
    sys.exit(app.exec_())
