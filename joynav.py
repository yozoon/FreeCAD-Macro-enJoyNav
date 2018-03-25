#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nav.py
#  

import FreeCAD, FreeCADGui, Part, math
import DraftVecUtils
import pivy
import time

from joy import ListenerThread

from pivy import coin
from FreeCAD import Base

try:
    from PySide import QtCore, QtGui
    FreeCAD.Console.PrintMessage("PySide is used" + "\n")
except:
    from PyQt4 import QtCore, QtGui
    FreeCAD.Console.PrintMessage("PyQt4 is needed" + "\n")

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s




import threading

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, cam):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.cam = cam

    def run(self):
        print "Starting " + self.name
        self.sequence(self.name)
        print "Exiting " + self.name

    def sequence(self, threadName):
        self.moveCenter(0.0, 0.0, 0.0)
        for i in range(0,360):
            r = 20.0+10.0*math.cos(4.0*math.radians(i))
            alpha = math.radians(i)
            beta = math.radians(45.0)
            gamma = math.radians(2*i)
            self.zoom(r)
            self.eulerRotation(alpha, beta, gamma)
            time.sleep(0.01)

    def moveCenter(self, x, y, z):
        self.cam.position = coin.SbVec3f(x, y, z)

    def zoom(self, d):
        self.cam.height.setValue(d)

    def eulerRotation(self, alpha, beta, gamma):
        x = coin.SbVec3f(1.0,0.0,0.0)
        y = coin.SbVec3f(0.0,1.0,1.0)
        z = coin.SbVec3f(0.0,0.0,1.0)

        r1 = coin.SbRotation()
        r1.setValue(z, alpha)

        r2 = coin.SbRotation()
        r2.setValue(x, beta)

        r3 = coin.SbRotation()
        r3.setValue(z, gamma)
        self.cam.orientation = r3*r2*r1


class Joynav(object):
    def __init__(self):
        super(Joynav, self).__init__()
        self.joyInterface = JoyInterface()
        #self.cam = Gui.ActiveDocument.ActiveView.getCameraNode()
        #self.listener = ListenerThread(1, self.cam)
        #self.listener.connect(0)

    def animate(self):
        thread1 = myThread(1, "Thread-1", 1, Gui.ActiveDocument.ActiveView.getCameraNode())
        thread1.start()

    def setupUi(self, Joynav):
        FCUi = FreeCADGui.UiLoader()

        # Window Properties
        Joynav.setObjectName(_fromUtf8("Joynav"))
        Joynav.resize(200, 200)
        Joynav.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        Joynav.setWindowTitle(QtGui.QApplication.translate("Joynav", "Joynav", None, QtGui.QApplication.UnicodeUTF8))
        
        # Button L
        self.Button_L = QtGui.QToolButton(Joynav)
        self.Button_L.setGeometry(QtCore.QRect(10, 75, 50, 50))
        self.Button_L.setObjectName(_fromUtf8("Button L"))
        self.Button_L.setText(QtGui.QApplication.translate("Joynav", "START", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.Button_L, QtCore.SIGNAL(_fromUtf8("pressed()")), self.buttonL)

        # Button R
        self.Button_R = QtGui.QToolButton(Joynav)
        self.Button_R.setGeometry(QtCore.QRect(140, 75, 50, 50))
        self.Button_R.setObjectName(_fromUtf8("Button R"))
        self.Button_R.setText(QtGui.QApplication.translate("Joynav", "STOP", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.Button_R, QtCore.SIGNAL(_fromUtf8("pressed()")), self.buttonR)

        # Button U
        self.Button_U = QtGui.QToolButton(Joynav)
        self.Button_U.setGeometry(QtCore.QRect(75, 10, 50, 50))
        self.Button_U.setObjectName(_fromUtf8("Button U"))
        self.Button_U.setText(QtGui.QApplication.translate("Joynav", "U", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.Button_U, QtCore.SIGNAL(_fromUtf8("pressed()")), self.buttonU)

        # Button R
        self.Button_D = QtGui.QToolButton(Joynav)
        self.Button_D.setGeometry(QtCore.QRect(75, 140, 50, 50))
        self.Button_D.setObjectName(_fromUtf8("Button D"))
        self.Button_D.setText(QtGui.QApplication.translate("Joynav", "ANIM", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.Button_D, QtCore.SIGNAL(_fromUtf8("pressed()")), self.buttonD)
        
        QtCore.QMetaObject.connectSlotsByName(Joynav)
  
    def buttonL(self):
        FreeCAD.Console.PrintMessage("Starting Input Listener!" + "\n")
        #self.listener.start()

    def buttonR(self):
        FreeCAD.Console.PrintMessage("Stopping input Listener!" + "\n")
        #self.listener.stop()

    def buttonU(self):
        FreeCAD.Console.PrintMessage("Button U Pressed!" + "\n")

    def buttonD(self):
        FreeCAD.Console.PrintMessage("Button D Pressed!" + "\n")
        #self.animate()
    
class JoynavMacro(object):
    d = QtGui.QWidget()
    d.ui = Joynav()
    d.ui.setupUi(d)
    if __name__ == '__main__':
        d.show()

def main():
    o = JoynavMacro()

if __name__ == '__main__':
    main()
