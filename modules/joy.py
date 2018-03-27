import FreeCAD
import os
import struct
import array
import threading
import math
import time
import pivy
import select
import fcntl

from pivy import coin
from fcntl import ioctl

from modules.operations import OperationClass

DEBUG = False
def dprint(str):
    if DEBUG:
        print(str)

# We'll store the states here.
axis_states = {}
button_states = {}

# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'trottle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

class JoyInterface(object):
    def __init__(self):
        super(JoyInterface, self).__init__()
        self.index = 0
        self.workerThread = None

    def findDevices(self):
        self.devices = []
        deviceNames = []
        # Iterate over the joystick devices.
        for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                device = '/dev/input/%s' % (fn)
                self.devices.append(device)
                deviceNames.append(self.getDeviceName(device))
        return [self.devices, deviceNames]

    def getDeviceName(self, device):
        try:
            # Open the joystick device.
            f = open(device, 'rb')
            # Get the device name.
            buf = array.array('b', [ord('\0')] * 64)
            ioctl(f, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
            f.close()
            return buf.tostring()
        except:
            # Retrieving devicename failed
            return []

    def connect(self,index=0):
        self.index = index
        try:
            # Open the joystick device.
            fn = self.devices[self.index] #'/dev/input/js0'
            #dprint('Opening %s...' % fn + '\n')
            jsdev = open(fn, 'rb')
        except:
            dprint("Opening device failed.")
            return [False, [], []]

        try:
            # Get the device name.
            buf = array.array('b', [ord('\0')] * 64)
            ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
            js_name = buf.tostring()
            
            # Get number of axes.
            buf = array.array('B', [0])
            ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
            num_axes = buf[0]
            
            # Get number of buttons.
            buf = array.array('B', [0])
            ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
            num_buttons = buf[0]
            
            # Get the axis map.
            buf = array.array('B', [0] * 0x40)
            ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP
                    
            self.axis_map = []
            for axis in buf[:num_axes]:
                axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
                self.axis_map.append(axis_name)
                axis_states[axis_name] = 0.0
                
            # Get the button map.
            buf = array.array('H', [0] * 200)
            ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP
            
            self.button_map = []
            for btn in buf[:num_buttons]:
                btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
                self.button_map.append(btn_name)
                button_states[btn_name] = 0
        except:
            dprint("Reading device info failed.")
            return [False, [], []]

        # Close file
        jsdev.close()

        return [True, self.axis_map, self.button_map]

    def startListening(self, operation_map, param_map, invert_map, cam):
        self.workerThread = WorkerThread(1, self.devices[self.index], self.axis_map, self.button_map, operation_map, param_map, invert_map, cam)
        self.workerThread.start()

    def resetView(self):
        if not self.workerThread == None:
            if self.workerThread.is_alive():
                self.workerThread.resetView()

    def exit(self):
        if not self.workerThread == None:
            if self.workerThread.is_alive():
                self.workerThread.exit()
                self.workerThread.join()


class WorkerThread (threading.Thread):
    def __init__(self, threadID, device, axis_map, button_map, operation_map, param_map, invert_map, cam):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = "WorkerThread"
        self.device = device
        self.exitFlag = 0
        self.cam = cam
        self.axis_map = axis_map
        self.button_map = button_map
        self.operationMap = operation_map
        self.paramMap = param_map
        self.invertMap = invert_map
        self.operationClass = OperationClass()
        self.operations = self.operationClass.getOperations()
        self.operationNames = self.operationClass.getOperationNames()

    def resetView(self):
        self.operationClass.resetView(self.cam)

    def updateOperationMap(self, operation_map):
        self.operationMap = operation_map

    def run(self):
        dprint("Thread started")
        dev = open(self.device, 'rb')
        while self.exitFlag == 0:
            # Check whether data is available
            r, w, e = select.select([ dev ], [], [], 0)
            
            # Read data if available
            evbuf = None
            if dev in r:
                evbuf = os.read(dev.fileno(), 8)

            if evbuf:
                t, value, type, number = struct.unpack('IhBB', evbuf)

                if type & 0x01:
                    button = self.button_map[number]
                    if button:
                        button_states[button] = value
                        if value:
                            dprint("%s pressed" % (button))
                        else:
                            dprint("%s released" % (button))

                if type & 0x02:
                    axis = self.axis_map[number]
                    if axis:
                        fvalue = value / 32767.0
                        axis_states[axis] = fvalue

            # Execute the operations
            self.executeOperations()
            time.sleep(0.001)

        dev.close()
        dprint("Thread ended")

    def executeOperations(self):
        for ax, value in self.operationMap.items():
            if self.invertMap[ax] == 0:
                self.operations[self.operationNames[value]](self.cam, axis_states[ax], self.paramMap[ax])
            else:
                self.operations[self.operationNames[value]](self.cam, axis_states[ax], -1.0 * self.paramMap[ax])

    def exit(self):
        self.exitFlag = 1
