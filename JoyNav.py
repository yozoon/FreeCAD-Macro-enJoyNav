import FreeCAD
import math
import time
import pivy

from pivy import coin
from FreeCAD import Base

from modules.joy import JoyInterface
from modules.operations import OperationClass

try:
    from PySide import QtCore, QtGui
except:
    from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

DEBUG = False
def dprint(str):
    if DEBUG:
        print(str)

operationMap = {}
paramMap = {}
invertMap = {}

class JoyNav(QtGui.QWidget):
    def __init__(self):
        super(JoyNav, self).__init__()
        # Window Properties
        self.width = 400
        self.height = 200
        self.setObjectName(_fromUtf8("JoyNav"))
        self.resize(self.width, self.height)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        self.setWindowTitle(QtGui.QApplication.translate("JoyNav", "JoyNav", None, QtGui.QApplication.UnicodeUTF8))

        self.joyInterface = JoyInterface()
        self.getDevices()
        self.operationClass = OperationClass()
        self.operationNames = self.operationClass.getOperationNames()
        self.operationMapping = {}
        self.setupUI()

    def closeEvent(self, event):
        self.joyInterface.exit()
        dprint("Closing")

    def getDevices(self):
        [self.deviceList, self.deviceNames] = self.joyInterface.findDevices()
        self.devicesAvailable = ( len(self.deviceList) > 0 )
        dprint(self.devicesAvailable)
        dprint(self.deviceList)

    def setupUI(self):
        # Main Layout Container
        self.mainLayout = QtGui.QVBoxLayout(self)

        # Device Layout Container
        self.devicesLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.devicesLayout)

        ## Not Connected Label
        self.notConnectedLabel = QtGui.QLabel()
        self.notConnectedLabel.setWordWrap(True)
        self.notConnectedLabel.setObjectName(_fromUtf8("NotConnectedLabel"))
        self.notConnectedLabel.setText(QtGui.QApplication.translate("NotConnectedLabel", 
            "Connection to device couldn\'t be established. Make sure the joystick is plugged in properly and then try again to connect.", None, QtGui.QApplication.UnicodeUTF8))

        # Retry Button
        self.retryButton = QtGui.QToolButton()
        self.retryButton.setObjectName(_fromUtf8("Retry Button"))
        self.retryButton.setText(QtGui.QApplication.translate("JoyNav", "Retry", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.retryButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.retryButtonPressed)

        ## Devices Label
        self.devicesLabel = QtGui.QLabel()
        self.devicesLabel.setWordWrap(True);
        self.devicesLabel.setObjectName(_fromUtf8("DevicesLabel"))
        self.devicesLabel.setText(QtGui.QApplication.translate("DevicesLabel", "Available Devices:", None, QtGui.QApplication.UnicodeUTF8))

        ## Device List ComboBox
        self.deviceSelect = QtGui.QComboBox()
        self.deviceSelect.setObjectName(_fromUtf8("DeviceSelect"))
        self.devicesLayout.addWidget(self.deviceSelect)
        
        # Connect Button
        self.connectButton = QtGui.QToolButton()
        self.connectButton.setObjectName(_fromUtf8("Connect Button"))
        self.connectButton.setText(QtGui.QApplication.translate("JoyNav", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.connectButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.connectButtonPressed)
        self.devicesLayout.addWidget(self.connectButton)

        # Start Button
        self.startButton = QtGui.QToolButton()
        self.startButton.setObjectName(_fromUtf8("Start Button"))
        self.startButton.setText(QtGui.QApplication.translate("JoyNav", "Start", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.startButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.startButtonPressed)

        # Reset View Button
        self.resetButton = QtGui.QToolButton()
        self.resetButton.setObjectName(_fromUtf8("Reset Button"))
        self.resetButton.setText(QtGui.QApplication.translate("JoyNav", "Reset View", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.resetButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.resetButtonPressed)

        ## Status Label
        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setWordWrap(True);
        self.statusLabel.setObjectName(_fromUtf8("StatusLabel"))
        self.statusLabel.setText(QtGui.QApplication.translate("StatusLabel", "", None, QtGui.QApplication.UnicodeUTF8))

        self.updateUI()

    def operationAssignmentUI(self, axisMap, buttonMap):
        self.devicesLayout.setParent(None)
        self.connectButton.hide()
        self.deviceSelect.hide()

        self.operationAssignmentLayout = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()

        label1 = QtGui.QLabel()
        label1.setFixedWidth(70)
        label1.setWordWrap(True)
        label1.setText(QtGui.QApplication.translate("JoyNav", "Axis Name", None, QtGui.QApplication.UnicodeUTF8))

        label2 = QtGui.QLabel()
        label2.setFixedWidth(230)
        label2.setWordWrap(True)
        label2.setText(QtGui.QApplication.translate("JoyNav", "Operation", None, QtGui.QApplication.UnicodeUTF8))

        label3 = QtGui.QLabel()
        label3.setFixedWidth(35)
        label3.setWordWrap(True)
        label3.setText(QtGui.QApplication.translate("JoyNav", "Invert", None, QtGui.QApplication.UnicodeUTF8))

        label4 = QtGui.QLabel()
        label4.setFixedWidth(155)
        label4.setWordWrap(True)
        label4.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label4.setText(QtGui.QApplication.translate("JoyNav", "Scaling", None, QtGui.QApplication.UnicodeUTF8))

        hbox.addWidget(label1)
        hbox.addStretch(1)
        hbox.addWidget(label2)
        hbox.addWidget(label3)
        hbox.addWidget(label4)
        self.operationAssignmentLayout.addLayout(hbox)

        for ax in axisMap:
            # Horizontal Layout
            hbox = QtGui.QHBoxLayout()

            index = self.operationNames.index("None")
            operationMap[ax] = index
            paramMap[ax] = 1.0
            invertMap[ax] = 0

            ## Axis Label
            label = QtGui.QLabel()
            label.setText(QtGui.QApplication.translate("JoyNav", ax+":", None, QtGui.QApplication.UnicodeUTF8))

            dropdown = QtGui.QComboBox()
            for i in range(len(self.operationNames)):
                dropdown.addItem(_fromUtf8(""))
                dropdown.setItemText(i, QtGui.QApplication.translate("JoyNav", self.operationNames[i], None, QtGui.QApplication.UnicodeUTF8))

            QtCore.QObject.connect(dropdown, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), OperationMappingCallback(ax))
            dropdown.setCurrentIndex(index)

            checkBox = QtGui.QCheckBox()
            checkBox.setChecked(False)
            QtCore.QObject.connect(checkBox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), InvertMappingCallback(ax))

            inputField = QtGui.QDoubleSpinBox()
            inputField.setValue(1.0)
            inputField.setSingleStep(0.1)
            QtCore.QObject.connect(inputField, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), ParamMappingCallback(ax))

            hbox.addWidget(label)
            hbox.addStretch(1)
            hbox.addWidget(dropdown)
            hbox.addWidget(checkBox)
            hbox.addWidget(inputField)
            self.operationAssignmentLayout.addLayout(hbox)

        self.mainLayout.addLayout(self.operationAssignmentLayout)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.startButton)
        hbox.addWidget(self.statusLabel)
        hbox.addWidget(self.resetButton)
        self.mainLayout.addLayout(hbox)

    def updateUI(self):
        # Update Device Select entries
        for i in range(len(self.deviceList)):
            self.deviceSelect.addItem(_fromUtf8(""))
            self.deviceSelect.setItemText(i, QtGui.QApplication.translate("DeviceSelect", self.deviceList[i] + ': ' + self.deviceNames[i], None, QtGui.QApplication.UnicodeUTF8))

        # Show/ hide UI elements
        if self.devicesAvailable:
            if not self.mainLayout.isEmpty():
                self.mainLayout.removeWidget(self.notConnectedLabel)
                self.notConnectedLabel.hide()
                self.mainLayout.removeWidget(self.retryButton)
                self.retryButton.hide()

            self.connectButton.show()
            self.deviceSelect.show()
        else:
            if not self.mainLayout.isEmpty():
                self.connectButton.hide()
                self.deviceSelect.hide()
            self.mainLayout.addWidget(self.notConnectedLabel)
            self.mainLayout.addWidget(self.retryButton)

    def retryButtonPressed(self):
        self.getDevices()
        self.updateUI()

    def connectButtonPressed(self):
        dprint("connect")
        self.axisMap = {}
        self.buttonMap = {}
        connectionSuccess = False
        if self.devicesAvailable:
            [connectionSuccess, self.axisMap, self.buttonMap] = self.joyInterface.connect(0)
            if connectionSuccess:
                dprint( 'axes found: %s' % (', '.join(self.axisMap)))
                dprint( 'buttons found: %s' % (', '.join(self.buttonMap)))
            else:
                dprint('Connection to device couldn\'t be established.')

        if connectionSuccess:
            self.operationAssignmentUI(self.axisMap, self.buttonMap)
        else:
            self.getDevices()
            self.updateUI()


    def startButtonPressed(self):
        self.getDevices()
        if self.devicesAvailable:
            success = False
            try:
                self.cam = Gui.ActiveDocument.ActiveView.getCameraNode()
                success = True
            except:
                dprint("No camera instance.")
                self.statusLabel.setText(QtGui.QApplication.translate("StatusLabel", 
                    "Please open a 3D view window and try again.", None, QtGui.QApplication.UnicodeUTF8))
            if success:
                dprint("Starting Input Listener!")
                dprint(operationMap)
                self.joyInterface.startListening(operationMap, paramMap, invertMap, self.cam)
                self.startButton.hide()
                self.statusLabel.setText(QtGui.QApplication.translate("StatusLabel", "Running. You can still change values and operation assignments.", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.updateUI()

    def resetButtonPressed(self):
        self.joyInterface.resetView()


##
# Helper classes to create dynamically created callback functions
##
class OperationMappingCallback:
    def __init__(self, name):
        self.name = name

    def __call__(self, index):
        operationMap[self.name] = index

class ParamMappingCallback:
    def __init__(self, name):
        self.name = name

    def __call__(self, num):
        paramMap[self.name] = num

class InvertMappingCallback:
    def __init__(self, name):
        self.name = name

    def __call__(self, b):
        invertMap[self.name] = b


class JoyNavMacro(object):
    d = JoyNav()
    if __name__ == '__main__':
        d.show()

def main():
    macro = JoyNavMacro()

if __name__ == '__main__':
    main()
