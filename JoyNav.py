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

DEBUG = True
def dprint(str):
    if DEBUG:
        print(str)

mapping = {}

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
        print("Closing")

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
        self.notConnectedLabel.setWordWrap(True);
        self.notConnectedLabel.setObjectName(_fromUtf8("NotConnectedLabel"))
        self.notConnectedLabel.resize(self.width, self.height)
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
        #self.devicesLabel.resize(self.width, self.height)
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

        # Update Button
        self.updateButton = QtGui.QToolButton()
        self.updateButton.setObjectName(_fromUtf8("Update Button"))
        self.updateButton.setText(QtGui.QApplication.translate("JoyNav", "Update", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.updateButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.updateButtonPressed)

        ## Status Label
        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setWordWrap(True);
        self.statusLabel.setObjectName(_fromUtf8("StatusLabel"))
        self.statusLabel.setText(QtGui.QApplication.translate("StatusLabel", "", None, QtGui.QApplication.UnicodeUTF8))

        self.updateUI()
        
        #QtCore.QMetaObject.connectSlotsByName(JoyNav)

    def operationAssignmentUI(self, axisMap, buttonMap):
        self.devicesLayout.setParent(None)
        self.connectButton.hide()
        self.deviceSelect.hide()

        self.operationAssignmentLayout = QtGui.QVBoxLayout()

        for ax in axisMap:
            # Horizontal Layout
            hbox = QtGui.QHBoxLayout()

            mapping[ax] = 0

            ## Axis Label
            label = QtGui.QLabel()
            label.setText(QtGui.QApplication.translate("JoyNav", ax+":", None, QtGui.QApplication.UnicodeUTF8))

            dropdown = QtGui.QComboBox()
            for i in range(len(self.operationNames)):
                dropdown.addItem(_fromUtf8(""))
                dropdown.setItemText(i, QtGui.QApplication.translate("JoyNav", self.operationNames[i], None, QtGui.QApplication.UnicodeUTF8))

            QtCore.QObject.connect(dropdown, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), MappingCallback(ax))
            index = self.operationNames.index("none")
            dropdown.setCurrentIndex(index)
            mapping[ax] = index
            # dropdown.setCurrentIndex(0)

            hbox.addWidget(label)
            hbox.addWidget(dropdown)
            self.operationAssignmentLayout.addLayout(hbox)

        self.mainLayout.addLayout(self.operationAssignmentLayout)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.startButton)
        hbox.addWidget(self.updateButton)
        self.updateButton.hide()
        hbox.addWidget(self.statusLabel)
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
            #self.mainLayout.addStretch(1)
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
                dprint(mapping)
                self.joyInterface.startListening(mapping, self.cam)
                self.startButton.hide()
                self.updateButton.show()
                self.statusLabel.setText(QtGui.QApplication.translate("StatusLabel", "Running", None, QtGui.QApplication.UnicodeUTF8))

        else:
            self.updateUI()

    def updateButtonPressed(self):
        self.joyInterface.updateOperationMap(mapping)


##
# Helper class to create dynamically created callback functions
##
class MappingCallback:
    def __init__(self, name):
        self.name = name

    def __call__(self, index):
        mapping[self.name] = index

class JoyNavMacro(object):
    d = JoyNav() #QtGui.QWidget()#
    if __name__ == '__main__':
        d.show()

def main():
    macro = JoyNavMacro()

if __name__ == '__main__':
    main()

#self.cam = Gui.ActiveDocument.ActiveView.getCameraNode()
#self.listener = ListenerThread(0, self.cam)
#self.listener.connect(0)

# import threading

# exitFlag = 0

# class myThread (threading.Thread):
#     def __init__(self, threadID, name, counter, cam):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.name = name
#         self.counter = counter
#         self.cam = cam

#     def run(self):
#         print "Starting " + self.name
#         self.sequence(self.name)
#         print "Exiting " + self.name

#     def sequence(self, threadName):
#         self.moveCenter(0.0, 0.0, 0.0)
#         for i in range(0,360):
#             r = 20.0+10.0*math.cos(4.0*math.radians(i))
#             alpha = math.radians(i)
#             beta = math.radians(45.0)
#             gamma = math.radians(2*i)
#             self.zoom(r)
#             self.eulerRotation(alpha, beta, gamma)
#             time.sleep(0.01)

#     def moveCenter(self, x, y, z):
#         self.cam.position = coin.SbVec3f(x, y, z)

#     def zoom(self, d):
#         self.cam.height.setValue(d)

#     def eulerRotation(self, alpha, beta, gamma):
#         x = coin.SbVec3f(1.0,0.0,0.0)
#         y = coin.SbVec3f(0.0,1.0,1.0)
#         z = coin.SbVec3f(0.0,0.0,1.0)

#         r1 = coin.SbRotation()
#         r1.setValue(z, alpha)

#         r2 = coin.SbRotation()
#         r2.setValue(x, beta)

#         r3 = coin.SbRotation()
#         r3.setValue(z, gamma)
#         self.cam.orientation = r3*r2*r1

#def animate(self):
    #    thread1 = myThread(1, "Thread-1", 1, Gui.ActiveDocument.ActiveView.getCameraNode())
    #    thread1.start()