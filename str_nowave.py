# STR Version 0.1.0
# Alex Ian Smith 2019

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
import threading
import os
import ntpath
from stretch import stretch0
import numpy
import webbrowser
import time
import wavio

class Process_function(QThread):
    # class var for stretch Results
    stretch_results = pyqtSignal(numpy.ndarray, int)

    def doit(self, data, fs, factor_value, buffer_value, offset_value,
    start_value, end_value, max_value):
        app.processEvents()
        #process the loaded wave data
        write_data, write_fs = stretch0(data, fs,
        factor_value, buffer_value, offset_value,
        start_value, end_value, max_value)
        # send results to 'receiveResults'
        self.stretch_results.emit(write_data, write_fs)

class External(QThread):
    # threaded processing for status text readout
    # I don't totally understand how this works yet.
    # class var
    messageChanged = pyqtSignal(str)

    def status(self, message):
        # function that actually updates the status
        self.messageChanged.emit(message)

class App(QWidget):

    def onButtonClick(self, message):
        # pass # print(message)
        self.calc = External()
        self.calc.messageChanged.connect(self.onMessageChanged)
        self.calc.status(message)

    def onMessageChanged(self, message):
        self.statuslabel.setText(message)

    def processClick(self):
        app.processEvents()
        self.update()

        self.click = Process_function()
        self.click.stretch_results.connect(self.receiveResults)
        self.click.doit(self.data, self.fs, self.factor_value,
        self.buffer_value, self.offset_value, self.start_value, self.end_value,
        self.max_value)

    def receiveResults(self, data, fs):
        # receives numpy array after being processed by stretch0
        if len(data) == 0:
            # if no data received
            self.onButtonClick('Error: Write Buffer Empty. Try again with different parameters')
        else:
            # if data received
            self.onButtonClick('')  # send which button clicked to status readout
            self.write_data = data  # assign data
            self.write_fs = fs      # assign rate
            self.saveFileDialog()   # call savefile dialog func

    def __init__(self):
        # initialize
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
        # set initial variable values on startup
        self.data = 0
        self.fs = 0
        self.factor_value = 1
        self.buffer_value = 0
        self.offset_value = 0
        self.start_value = 0
        self.end_value = 99
        self.max_value = 0.0165
        self.filename = 0

    def initUI(self):
        # initialize UI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.layout = QGridLayout()     # establish layout
        self.layout.setSpacing(10)      # set global spacing

        # add buttons to layout

        self.layout.addWidget(self.filelabel, 11, 0, 2, 2)
        self.layout.addWidget(self.openbutton, 12, 2)
        self.layout.addWidget(self.randombutton, 12, 6)
        self.layout.addWidget(self.processbutton, 12, 7)
        self.layout.addWidget(self.aboutbutton, 12, 11)

        # add labels to Layout
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

        # add sliders to layout

        self.statuslabel = QLabel('')
        self.layout.addWidget(self.statuslabel, 13, 2, 1, 10)

        self.setLayout(self.layout)
        self.update()

        self.show()

    def initbuttons(self):
        # initialize buttons
        # open
        self.openbutton = QPushButton("Open", self)
        self.openbutton.setToolTip('Open a Wav file')
        self.openbutton.clicked.connect(self.openFileNameDialog)

        # random
        self.randombutton = QPushButton("Random", self)
        self.randombutton.setToolTip('Randomize settings')
        self.randombutton.clicked.connect(self.randomize)

        # process
        self.processbutton = QPushButton("Process", self)
        self.processbutton.setToolTip('Processes Wav file')
        self.processbutton.clicked.connect(self.process)

        # about
        self.aboutbutton = QPushButton("About", self)
        self.aboutbutton.clicked.connect(self.aboutdialog)

    def initsliders(self):
        # initialize Sliders and labels
        # factor
        self.factorslider = QSlider(Qt.Horizontal)
        self.factorslider.setMinimum(-100)
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

        # loaded filename display
        self.filelabel = QLabel("\n\n")

    def open_webbrowser(self):
        # func to open website
        webbrowser.open('http://alexiansmith.com')

    def factor(self):
        # func for factor slider
        self.update()
        self.factor_value = self.factorslider.value()
        self.factorlabel.setText('Factor:\n' + str(self.factor_value))

    def buf(self):
        # func for buffer slider
        self.update()
        self.buffer_value = float(self.bufslider.value()/1000)
        self.buflabel.setText('Buffer:\n' + str(self.buffer_value))

    def offset(self):
        # func for offset slider
        self.offset_value = float(self.offsetslider.value()/1000)
        self.offsetlabel.setText('Offset:\n' + str(self.offset_value))

    def start(self):
        # func for start slider
        self.start_value = self.startslider.value()
        self.startlabel.setText('Start:\n' + str(self.start_value))

    def end(self):
        # func for end slider
        self.end_value = self.endslider.value()
        self.endlabel.setText('End:\n' + str(self.end_value))

    def max(self):
        # func for max sliders
        min = int(self.maxslidermin.value())
        sec = float((self.maxslidersec.value())/100)
        self.max_value = (min + sec/60)
        self.maxlabel.setText(f"Max Length:\n{str(min)} min {str(sec)} sec")
        if self.max_value > 1.5:
            # warning about longer outputs
            self.onButtonClick("Careful! more than a couple minutes can take A LOT of time and computer resources to process")
        else:
            self.onButtonClick('')

    def open(self):
        # loads wave file to memory
        try:
            wavein = wavio.read(self.filename)
            self.data = wavein.data
            self.fs = wavein.rate
            self.swidth = wavein.sampwidth
            # updates file label
            self.filelabel.setText("File Loaded:\n" + ntpath.basename(self.filename))
            self.filelabel.setAlignment(Qt.AlignRight)
        except:
            self.onButtonClick("Couldn't load wav file")

    def randomize(self):
        # randomizes values
        self.update()
        self.f = random.uniform(-50, 50)
        self.b = random.uniform(0, 49000)
        self.o = random.uniform(0, 1000)
        self.s = random.uniform(0, 60)
        self.update()
        # applies values to slider display
        self.factorslider.setValue(self.f)
        self.bufslider.setValue(self.b)
        self.offsetslider.setValue(self.o)
        self.startslider.setValue(self.s)
        self.e = random.uniform((self.startslider.value() + 1), 99)
        self.endslider.setValue(self.e)
        self.update()

    def process(self):
        # Process button clicked
        if self.start_value > self.end_value:
            self.onButtonClick("Startpoint cannot be larger than Endpoint")
        else:
            # update status label
            self.onButtonClick("Processing...   STR will be unresponsive until Process completes")
            self.processClick()     # call processClick function to process data
            self.update()

    def revert_processing(self):
        # resets status label when processing is complete
        self.onButtonClick('')

    def save(self):
        # saves processed data to a wave file


        try:
            wavio.write(self.save_filename, self.write_data, self.write_fs)
            # status label readout
            self.onButtonClick(f"{ntpath.basename(self.save_filename)} saved")
        except:
            self.onButtonClick(f"save error: couldn't save {ntpath.basename(self.save_filename)}")

    def openFileNameDialog(self):
        # open dialog
        home = str(Path.home())     # not sure if this works...
        # base_dir = os.path.dirname(os.path.abspath(__file__)) leaving this code in for future testing
        # call dialog & set selected file to self.filename
        self.filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","",home,"Wav Files (*.wav)")
        if self.filename:
            self.open()

    def ReadMe(self):
        # opens readme in a text editor
        os.system('open ReadMe.md')

    def aboutdialog(self):
        # opens a new window for about section
        self.aboutwindow = QDialog()

        # define buttons
        b1 = QPushButton("alexiansmith.com",self.aboutwindow)
        b1.clicked.connect(self.open_webbrowser)
        b2 = QPushButton("Close")
        b2.clicked.connect(self.aboutwindow.close)
        b3 = QPushButton("ReadMe")
        b3.clicked.connect(self.ReadMe)
        # fix this so it just reads the selected lines from the readme file
        l1 = QLabel("STR is an application for manipulating '.wav' files\nfor creative and sometimes unexpected results\n\n © Alex Ian Smith 2019\n\n")

        # add buttons & labels to layout
        abt = QVBoxLayout()
        abt.addWidget(l1)
        abt.addStretch()
        abt.addWidget(b3)
        abt.addWidget(b1)
        abt.addWidget(b2)

        # set layout
        self.aboutwindow.setLayout(abt)
        self.aboutwindow.setWindowTitle("About")
        self.aboutwindow.setWindowModality(Qt.ApplicationModal)
        self.aboutwindow.exec_()

    def saveFileDialog(self):
        # opens save file dialog
        try:
            if self.write_fs:
                # options = QFileDialog.Options()
                # options |= QFileDialog.DontUseNativeDialog
                home = str(Path.home())
                self.save_filename, _ = QFileDialog.getSaveFileName(self,"Save","",home,"Wav Files (*.wav)")
                if self.save_filename:
                    # pass # print(self.save_filename)
                    self.save()
        except:
            self.onButtonClick("Nothing to save. Process something first")

if __name__ == '__main__':
    # it's main. the actual program loop
    app = QApplication(sys.argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.setWindowIcon(QIcon(base_dir + '/STR-icon.png'))
    ex = App()
    app.setStyle('Fusion')
    sys.exit(app.exec_())
