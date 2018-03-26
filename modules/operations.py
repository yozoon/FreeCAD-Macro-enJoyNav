import math
import pivy
from pivy import coin

x = coin.SbVec3f(1.0,0.0,0.0)
y = coin.SbVec3f(0.0,1.0,1.0)
z = coin.SbVec3f(0.0,0.0,1.0)

def dummy(cam, arg):
    return

def moveCenterX(cam, arg):
    [X, Y, Z, W] = currentRotationQuaternions(cam)
    [alpha, beta, gamma] = quaternionToEulerAngle(X,Y,Z,W)
    cam.orientation = eulerRotation(alpha, beta, gamma)

def moveCenterY(cam, arg):
    print('move_center_y')

def moveCenterZ(cam, arg):
    print('move_center_z')

def rotateCenterX(cam, arg):
    print('rotate_center_x')

def rotateCenterY(cam, arg):
    print('rotate_center_y')

def rotateCenterZ(cam, arg):
    print('rotate_center_z')

def rotateCameraX(cam, arg):
    print('rotate_camera_x')

def rotateCameraY(cam, arg):
    print('rotate_camera_y')

def rotateCameraZ(cam, arg):
    print('rotate_camera_z')

def rotateCamerasystemCenterX(cam, arg):
    r = coin.SbRotation()
    r.setValue(x, math.radians(arg))
    cam.orientation = r*currentRotation(cam)

def rotateCamerasystemCenterY(cam, arg):
    r = coin.SbRotation()
    r.setValue(y, math.radians(arg))
    cam.orientation = r*currentRotation(cam)

def rotateCamerasystemCenterZ(cam, arg):
    [X, Y, Z, W] = currentRotationQuaternions(cam)
    quaternionToEulerAngle(X,Y,Z,W)
    r = coin.SbRotation()
    r.setValue(z, math.radians(arg))
    cam.orientation = r*currentRotation(cam)

def zoom(cam, arg):
    # SoSFFloat Object
    r = cam.height.getValue()
    #r = r.getValue()
    cam.height.setValue(r+arg)



def currentPosition(cam):
    cam.position.getValue()

def currentRotation(cam):
    rot = cam.orientation.getValue() 
    return coin.SbRotation(rot.getValue())

def currentRotationQuaternions(cam):
    [X, Y, Z, W] = cam.orientation.getValue().getValue()
    return [X, Y, Z, W]

def eulerRotation(alpha, beta, gamma):
    r1 = coin.SbRotation()
    r1.setValue(z, alpha)

    r2 = coin.SbRotation()
    r2.setValue(x, beta)

    r3 = coin.SbRotation()
    r3.setValue(z, gamma)
    return r3*r2*r1

# Based on http://bediyap.com/programming/convert-quaternion-to-euler-rotations/
def quaternionToEulerAngle(X,Y,Z,W):
    r11 = 2*(X*Z + W*Y)      
    r12 = -2*(Y*Z - W*X)
    r21 = W*W - X*X - Y*Y + Z*Z      
    r31 = 2*(X*Z - W*Y)
    r32 = 2*(Y*Z + W*X)

    alpha = math.atan2( r11, r12 );
    beta = math.acos ( r21 );
    gamma = math.atan2( r31, r32 );

    return [alpha, beta, gamma]

operations = {
    'none': dummy,
    'move_center_x': moveCenterX,
    'move_center_y': moveCenterY,
    'move_center_z': moveCenterZ,
    'rotate_center_x': rotateCenterX,
    'rotate_center_y': rotateCenterY,
    'rotate_center_z': rotateCenterZ,
    'rotate_camera_x': rotateCameraX,
    'rotate_camera_y': rotateCameraY,
    'rotate_camera_z': rotateCameraZ,
    'rotate_camerasystem_center_x': rotateCamerasystemCenterX,
    'rotate_camerasystem_center_y': rotateCamerasystemCenterY,
    'rotate_camerasystem_center_z': rotateCamerasystemCenterZ,
    'zoom': zoom
}

# operations['rotate_center_x']('',10.0)


class OperationClass(object):
    def getOperationNames(self):
        return operations.keys()
    def getOperations(self):
        return operations