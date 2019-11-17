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

import sys
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QPlainTextEdit,
QInputDialog, QLineEdit, QFileDialog, QSlider, QDialog, QVBoxLayout, QLabel,
QGridLayout, QStatusBar, QToolButton, QHBoxLayout, QStyleFactory, QMainWindow,
QShortcut)
from PyQt5.QtGui import QIcon, QFont, QKeySequence
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
    # I don't totally understand how this works yet, but it does.
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
        self.processString()
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
        self.width = 400
        self.height = 200
        self.colwidth = 110
        # self.setFixedSize(self.width, self.height)
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
        self.save_filename = 'untitled'

    def initUI(self):
        # initialize UI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.setFixedSize(self.width, self.height)
        self.layout = QGridLayout()     # establish layout
        self.layout.setSpacing(12)      # set global spacing

        # add labels to Layout
        self.layout.addWidget(self.labelbox, 6, 2, 3, 4)
        # self.layout.addWidget(self.factorlabel, 1, 3, 1, 3)
        # self.layout.addWidget(self.buflabel, 2, 3, 1, 3)
        # self.layout.addWidget(self.offsetlabel, 3, 3, 1, 3)
        # self.layout.addWidget(self.startlabel, 4, 3, 1, 3)
        # self.layout.addWidget(self.endlabel, 5, 3, 1, 3)

        self.layout.addWidget(self.inputbox, 1, 1)
        self.layout.addWidget(self.maxslidersec, 3, 1)
        self.layout.addWidget(self.maxslidermin, 2, 1)
        self.layout.addWidget(self.maxlabel, 4, 1, 1, 2)
        self.layout.addWidget(self.filelabel, 5, 2, 1, 4)
        self.layout.addWidget(self.openbutton, 5, 1)
        # self.layout.addWidget(self.randombutton, 13, 2)
        self.layout.addWidget(self.processbutton, 6, 1)
        self.layout.addWidget(self.aboutbutton, 7, 1)
        self.layout.addWidget(self.statuslabel, 1, 2, 3, 4)
        self.setLayout(self.layout)
        self.update()

        self.show()

    def initbuttons(self):
        # initialize buttons
        # open
        self.openbutton = QPushButton("Open", self)
        self.openbutton.clicked.connect(self.openFileNameDialog)
        self.openbutton.setFixedWidth(self.colwidth)

        self.shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut.activated.connect(self.openFileNameDialog)

        # random
        # self.randombutton = QPushButton("Random", self)
        # self.randombutton.clicked.connect(self.randomize)

        # process
        self.processbutton = QPushButton("Process", self)
        self.processbutton.clicked.connect(self.process)
        self.processbutton.setFixedWidth(self.colwidth)
        self.processbutton.setEnabled(False)

        # about
        self.aboutbutton = QPushButton("About", self)
        self.aboutbutton.clicked.connect(self.aboutdialog)
        self.aboutbutton.setFixedWidth(self.colwidth)

    def initsliders(self):
        # initialize Sliders and labels
        self.labelbox = QLabel(self)
        self.labelbox.setText('')
        self.labelbox.setWordWrap(True)
        self.labelbox.setAlignment(Qt.AlignRight)
        # factor
        self.factorslider = QSlider(Qt.Horizontal)
        self.factorslider.setMinimum(-100)
        self.factorslider.setMaximum(100)
        self.factorslider.setValue(1)
        self.factorslider.valueChanged.connect(self.factor)
        self.factorlabel = QLabel('1')
        self.factorlabel.setAlignment(Qt.AlignRight)
        # self.factorlabel.setFixedWidth(self.colwidth)

        # buffer
        self.bufslider = QSlider(Qt.Horizontal)
        self.bufslider.setMinimum(0)
        self.bufslider.setMaximum(59999)
        self.bufslider.setValue(0)
        self.bufslider.setSingleStep(1)
        self.bufslider.valueChanged.connect(self.buf)
        self.buflabel = QLabel('0')
        self.buflabel.setAlignment(Qt.AlignRight)
        # self.buflabel.setFixedWidth(self.colwidth)

        # offset
        self.offsetslider = QSlider(Qt.Horizontal)
        self.offsetslider.setMinimum(0)
        self.offsetslider.setMaximum(1000)
        self.offsetslider.setValue(0)
        self.offsetslider.setSingleStep(1)
        self.offsetslider.valueChanged.connect(self.offset)
        self.offsetlabel = QLabel('0')
        self.offsetlabel.setAlignment(Qt.AlignRight)
        # self.offsetlabel.setFixedWidth(self.colwidth)

        # startpoint
        self.startslider = QSlider(Qt.Horizontal)
        self.startslider.setMinimum(0)
        self.startslider.setMaximum(99)
        self.startslider.setValue(0)
        self.startslider.setSingleStep(1)
        self.startslider.valueChanged.connect(self.start)
        self.startlabel = QLabel('0')
        self.startlabel.setAlignment(Qt.AlignRight)
        # self.startlabel.setFixedWidth(self.colwidth)

        # endpoint
        self.endslider = QSlider(Qt.Horizontal)
        self.endslider.setMinimum(0)
        self.endslider.setMaximum(99)
        self.endslider.setValue(99)
        self.endslider.setSingleStep(1)
        self.endslider.valueChanged.connect(self.end)
        self.endlabel = QLabel('99')
        self.endlabel.setAlignment(Qt.AlignRight)
        # self.endlabel.setFixedWidth(self.colwidth)

        # max size
        self.maxslidermin = QSlider(Qt.Horizontal)
        self.maxslidermin.setMinimum(0)
        self.maxslidermin.setMaximum(59)
        self.maxslidermin.setValue(0)
        self.maxslidermin.setSingleStep(1)
        self.maxslidermin.valueChanged.connect(self.max)
        self.maxslidermin.setFixedWidth(self.colwidth)
        self.maxslidersec = QSlider(Qt.Horizontal)
        self.maxslidersec.setMinimum(0)
        self.maxslidersec.setMaximum(5999)
        self.maxslidersec.setValue(99)
        self.maxslidersec.setSingleStep(1)
        self.maxslidersec.valueChanged.connect(self.max)
        self.maxslidersec.setFixedWidth(self.colwidth)
        self.maxlabel = QLabel('Max Length: 0 min 0.99 sec')
        # self.maxlabel.setFixedWidth(self.colwidth)
        self.inputbox = QLineEdit(self)
        self.inputbox.setMaxLength(7)
        self.inputbox.setFixedWidth(self.colwidth)
        self.inputbox.textChanged.connect(self.processString)
        self.inputbox.setFocusPolicy(Qt.StrongFocus)
        self.inputbox.returnPressed.connect(self.process)

        # loaded filename display
        self.filelabel = QLabel('No File Loaded.')
        self.filelabel.setAlignment(Qt.AlignLeft)

        # status
        self.statuslabel = QLabel('')
        self.statuslabel.setWordWrap(True)
        self.statuslabel.setAlignment(Qt.AlignRight)


    def open_webbrowser(self):
        # func to open website
        webbrowser.open('http://alexiansmith.com')
##########################################
    def factor(self):
        # func for factor slider
        # self.update()
        # self.factor_value = self.factorslider.value()
        self.factorlabel.setText(str(self.factor_value))

    def buf(self):
        # func for buffer slider
        # self.update()
        # self.buffer_value = float(self.bufslider.value()/1000)
        self.buflabel.setText(str(self.buffer_value))

    def offset(self):
        # func for offset slider
        # self.offset_value = float(self.offsetslider.value()/1000)
        self.offsetlabel.setText(str(self.offset_value))

    def start(self):
        # func for start slider
        # self.start_value = self.startslider.value()
        self.startlabel.setText(str(self.start_value))

    def end(self):
        # func for end slider
        # self.end_value = self.endslider.value()
        self.endlabel.setText(str(self.end_value))

    def max(self):
        # func for max sliders
        min = int(self.maxslidermin.value())
        sec = float((self.maxslidersec.value())/100)
        self.max_value = (min + sec/60)
        self.maxlabel.setText(f"Max Length: {str(min)} min {str(sec)} sec")
        if self.max_value > 1.5:
            # warning about longer outputs
            self.onButtonClick("Careful! Long Wav Files have Long Process Times!")
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
            self.filelabel.setText("File Loaded: " + ntpath.basename(self.filename))
            self.onButtonClick(f"{ntpath.basename(self.filename)} loaded")
            self.processbutton.setEnabled(True)
        except:
            self.onButtonClick("Couldn't load wav file")
            self.setprocessbutton.setenabled(False)

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

    def processString(self):
        string = self.inputbox.text()
        # ensure wave data is loaded
        if isinstance(self.data, int):
            self.onButtonClick('')
        if len(string) < 1:
            self.onButtonClick('')
            self.factor_value = 1
            self.buffer_value = 0
            self.offset_value = 0
            self.start_value = 0
            self.end_value = 99
            self.save_filename = 'untitled'
            # self.buf()
            # self.factor()
            # self.offset()
            # self.start()
            # self.end()
            self.labelbox.setText('')
        else:
            # process string input
            if len(string) < 7:
                string = string * 7
            string = string[0:7]
            self.save_filename = string
            self.num_string = list()
            for i in range(len(string)):
                # adjust values so range is 0 - 8836
                if i == (len(string) - 1):
                    # self.num_string.append(ord(string[i]) - 33) * (ord(string[0]) - 33)
                    a = ord(string[i]) - 32
                    b = ord(string[0]) - 32
                    self.num_string.append(a * b)
                else:
                    # self.num_string.append(ord(string[i]) - 33) * (ord(string[i+1]) - 33)
                    a = ord(string[i]) - 32
                    b = ord(string[-1]) - 32
                    self.num_string.append(a * b)
            self.num_string[1] = (ord(string[1]) - 32) * (ord(string[2]) - 32)
            self.num_string[2] = (ord(string[2]) - 32) * (ord(string[0]) - 32)

            print("self.num_string list:\n", self.num_string)

            # calculate Params from string
            self.factor_value = (ord(string[0]) - 32) - 47    # constrain -47 - 47
            print("factor", self.factor_value)
            self.factor()
            if self.num_string[1] == 0:
                bufsize_infine = 0
            else:
                bufsize_infine = self.num_string[1] / 9025.0 # constrain to 0 - 1
            print("bufsize_infine", bufsize_infine)
            if self.num_string[2] == 0:
                self.buffer_value = 0
            else:
                self.buffer_value = bufsize_infine + (self.num_string[2] / 90.25) # constrain to 0 - 99
            print("buffer", self.buffer_value)
            self.buf()
            offset_fine = self.num_string[3] / 88360.0   # constrain 0 - 0.1
            print("offset_fine", offset_fine)
            self.offset_value = offset_fine + self.num_string[4] / 90.25  # constrain 0 - 99
            print("self.offset_value", self.offset_value)
            self.offset()
            self.start_value = 0
            self.end_value = 99
            self.start_value = int(self.num_string[5] / 90.25)    # constrain to 0 - 99
            print("self.startvalue", self.start_value)
            self.end_value = int(99 - self.num_string[6] / 90.25)
            print("self.end_value", self.end_value)
            if self.end_value > 98:
                while self.start_value >= self.end_value:
                    self.start_value = self.start_value - 1
            else:
                if self.start_value >= self.end_value:
                    for i in range(len(string)):
                        self.end_value = int(99 - self.num_string[i] / 90.25)
                        if self.end_value > self.start_value:
                            break
                while self.start_value >= self.end_value:
                    self.end_value = self.end_value + 1
            self.start()
            self.end()
            self.labelbox.setText(f"{self.num_string} {self.factor_value} {self.buffer_value} {self.offset_value} {self.start_value} {self.end_value} ")


    def process(self):
        # (self.data, self.fs, self.factor_value, self.buffer_value,
        # self.offset_value, self.start_value, self.end_value, self.max_value)
        # Process button clicked
        if isinstance(self.data, int):
            self.onButtonClick('Nothing to process, load a wav file first')
        elif isinstance(self.data, numpy.ndarray):
            if self.start_value >= self.end_value:
                self.onButtonClick("Startpoint cannot be larger than Endpoint")
            else:
                # update status label
                self.onButtonClick("Processing... STR will be unresponsive untill process is complete")
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
        # home = str(Path.home())     # not sure if this works...
        # base_dir = os.path.dirname(os.path.abspath(__file__)) leaving this code in for future testing
        # call dialog & set selected file to self.filename
        home = (os.path.expanduser('~'))
        print(home)
        self.filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","",home,"Wav Files (*.wav)")
        if self.filename:
            self.open()


    def ReadMe(self):
        # opens readme in a text editor
        # os.system('open ReadMe.md')
        readme = R

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
        l1 = QLabel("1. Open wave file\n2. Type something in text box\n3. Process\n\n © Alex Ian Smith 2019\n\n")

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
            if self.write_fs and self.save_filename != 0:
                # options = QFileDialog.Options()
                # options |= QFileDialog.DontUseNativeDialog
                home = str(Path.home())
                while True:
                    if os.path.isfile(self.save_filename + '.wav') == 1:
                        self.save_filename = self.save_filename + '0'
                        # self.save_filename, _ = QFileDialog.getSaveFileName(self,"Save","",home,"Wav Files (*.wav)")
                    else:
                        break
                self.save_filename = self.save_filename + '.wav'
                if self.save_filename:
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
