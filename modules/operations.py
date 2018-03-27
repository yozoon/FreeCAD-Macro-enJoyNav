import math
import pivy
from pivy import coin

x = coin.SbVec3f(1.0,0.0,0.0)
y = coin.SbVec3f(0.0,1.0,0.0)
z = coin.SbVec3f(0.0,0.0,1.0)

def dummy(cam, arg, param=1):
    return

def moveCenterX(cam, arg, param=1):
    [X, Y, Z] = currentPosition(cam)
    cam.position = coin.SbVec3f(X + arg * param, Y, Z)

def moveCenterY(cam, arg, param=1):
    [X, Y, Z] = currentPosition(cam)
    cam.position = coin.SbVec3f(X, Y + arg * param, Z)

def moveCenterZ(cam, arg, param=1):
    [X, Y, Z] = currentPosition(cam)
    cam.position = coin.SbVec3f(X, Y, Z + arg * param)

def rotateCenterX(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(x, math.radians(arg * param))
    cam.orientation = currentRotation(cam) * r

def rotateCenterY(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(y, math.radians(arg * param))
    cam.orientation = currentRotation(cam) * r

def rotateCenterZ(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(z, math.radians(arg * param))
    cam.orientation = currentRotation(cam) * r

def rotateCamerasystemCenterX(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(x, math.radians(arg * param))
    cam.orientation = r*currentRotation(cam)

def rotateCamerasystemCenterY(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(y, math.radians(arg * param))
    cam.orientation = r*currentRotation(cam)

def rotateCamerasystemCenterZ(cam, arg, param=1):
    r = coin.SbRotation()
    r.setValue(z, math.radians(arg * param))
    cam.orientation = r*currentRotation(cam)

def zoom(cam, arg, param=1):
    r = cam.height.getValue()
    cam.height.setValue(r + arg * param)

operations = {
    'None': dummy,
    'Move Center X': moveCenterX,
    'Move Center Y': moveCenterY,
    'Move Center Z': moveCenterZ,
    'Rotate X': rotateCenterX,
    'Rotate Y': rotateCenterY,
    'Rotate Z': rotateCenterZ,
    'Rotate Camerasystem Center X': rotateCamerasystemCenterX,
    'Rotate Camerasystem Center Y': rotateCamerasystemCenterY,
    'Rotate Camerasystem Center Z': rotateCamerasystemCenterZ,
    'Zoom': zoom
}


###############################
# Helper Functions
###############################
def currentPosition(cam):
    return cam.position.getValue()

def currentRotation(cam):
    rot = cam.orientation.getValue() 
    return coin.SbRotation(rot.getValue())

def currentRotationQuaternions(cam):
    [X, Y, Z, W] = cam.orientation.getValue().getValue()
    return [X, Y, Z, W]

def eulerRotationZXZ(alpha, beta, gamma):
    r1 = coin.SbRotation()
    r1.setValue(z, alpha)

    r2 = coin.SbRotation()
    r2.setValue(x, beta)

    r3 = coin.SbRotation()
    r3.setValue(z, gamma)
    return r3*r2*r1

def eulerRotationXYX(alpha, beta, gamma):
    r1 = coin.SbRotation()
    r1.setValue(x, alpha)

    r2 = coin.SbRotation()
    r2.setValue(y, beta)

    r3 = coin.SbRotation()
    r3.setValue(x, gamma)
    return r3*r2*r1

# Based on http://bediyap.com/programming/convert-quaternion-to-euler-rotations/
def quaternionToEulerAngleZXZ(X,Y,Z,W):
    r11 = 2*(X*Z + W*Y)      
    r12 = -2*(Y*Z - W*X)
    r21 = W*W - X*X - Y*Y + Z*Z      
    r31 = 2*(X*Z - W*Y)
    r32 = 2*(Y*Z + W*X)
    return twoaxisrot(r11, r12, r21, r31, r32)

def quaternionToEulerAngleXYX(X,Y,Z,W):
    r11 = 2*(X*Y + W*Z)
    r12 = -2*(X*Z - W*Y)
    r21 = W*W + X*X - Y*Y - Z*Z
    r31 = 2*(X*Y - W*Z)
    r32 = 2*(X*Z + W*Y)
    return twoaxisrot(r11, r12, r21, r31, r32)

def twoaxisrot(r11, r12, r21, r31, r32):
    alpha = math.atan2( r11, r12 );
    beta = math.acos ( confine(r21, 0.0, 1.0) )
    gamma = math.atan2( r31, r32 );
    return [alpha, beta, gamma]

def clamp(value, vmin, vmax):
    return max(min(value, vmax), vmin)

def confine(value, vmin, vmax):
    rang = vmax - vmin
    tmp = value - vmin
    mod = tmp % rang
    return vmin + mod



class OperationClass(object):
    def getOperationNames(self):
        return operations.keys()
    def getOperations(self):
        return operations