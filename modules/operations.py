def dummy(cam, arg):
	return

def moveCenterX(cam, arg):
    print('move_center_x')

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
    print('rotate_camerasystem_center_x')

def rotateCamerasystemCenterY(cam, arg):
    print('rotate_camerasystem_center_y')

def rotateCamerasystemCenterZ(cam, arg):
    print('rotate_camerasystem_center_z')

def zoom(cam, arg):
    print('zoom')

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
	'rotate_camerasystem_center_z': rotateCamerasystemCenterX,
	'zoom': zoom
}

# operations['rotate_center_x']('',10.0)


class OperationClass(object):
    def getOperationNames(self):
    	return operations.keys()
    def getOperations(self):
    	return operations