import sys
from ctypes import *
import threading
import time

def PeriodicTask():
    dll.PeriodicTask()
    threading.Timer(0.5, PeriodicTask).start()

def GetPoseTask():
    pose = Pose()
    dll.GetPose(byref(pose))
    #print 'Pose:', pose.x, pose.y, pose.z, pose.rHead, pose.joint1Angle, pose.joint2Angle, pose.joint3Angle, pose.joint4Angle
    threading.Timer(0.5, GetPoseTask).start()

# For initial pose
class InitialPose(Structure):
    _fields_ = [("joint2Angle", c_float), ("joint3Angle", c_float)]

# For pose
class Pose(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("rHead", c_float),
        ("joint1Angle", c_float),
        ("joint2Angle", c_float),
        ("joint3Angle", c_float),
        ("joint4Angle", c_float),
        ("isGrab", c_byte),
        ("gripper", c_float)
        ]

# For jog
class JogStaticParams(Structure):
    _fields_ = [
        ("jointMaxVelocity", c_float), ("jointMaxAcceleration", c_float),
        ("servoMaxVelocity", c_float), ("servoMaxAcceleration", c_float),
        ("linearMaxVelocity", c_float), ("linearMaxAcceleration", c_float)
        ]

class JogDynamicParams(Structure):
    _fields_ = [("velocityRatio", c_float)]

class JogInstantCmd(Structure):
    _fields_ = [("isJoint", c_byte), ("cmd", c_int)]

class PlaybackStaticParams(Structure):
    _fields_ = [
        ("jointMaxVelocity", c_float), ("jointMaxAcceleration", c_float),
        ("servoMaxVelocity", c_float), ("servoMaxAcceleration", c_float),
        ("linearMaxVelocity", c_float), ("linearMaxAcceleration", c_float),
    ]

class PlaybackDynamicParams(Structure):
    _fields_ = [("velocityRatio", c_float), ("accelerationRatio", c_float)]


class PlaybackBufferCmd(Structure):
    _fields_ = [
        ("motionStyle", c_byte), ("isGrab", c_byte),
        ("x", c_float), ("y", c_float), ("z", c_float), ("rHead", c_float),
        ("gripper", c_float), ("pauseTime", c_float)
    ]

class PlaybackAngleBufferCmd(Structure):
    _fields_ = [
        ("motionStyle", c_byte), ("isGrab", c_byte),
        ("joint1", c_float), ("joint2", c_float), ("joint3", c_float), ("joint4", c_float),
        ("gripper", c_float), ("pauseTime", c_float)
    ]


if __name__ == "__main__":
    sys.path.append(sys.path[0])
    dll = cdll.LoadLibrary(sys.path[0] + '//DobotDll.dll');
    PeriodicTask()
    GetPoseTask()

    errorString = [
        'Success',
        'Warning:Long arm angle not good!',
        'Warning:Short arm angle not good!',
        'Both long & short arm angle not good!',
        'Error:Dobot not found!',
        "Error:COM port occupied!",
        "Error:No data uploaded!"
        ]

    result = dll.ConnectDobot()
    print errorString[result]

    if (result < 4):
        # Set command timeout
        dll.SetCmdTimeout(3000)
        # Set initial pose
        '''
        initialPose = InitialPose()
        initialPose.joint2Angle = 45
        initialPose.joint3Angle = 45
        dll.SetInitialPose.argtypes = [POINTER(InitialPose)]
        dll.SetInitialPose(byref(initialPose))
        '''

        pbsParam = PlaybackStaticParams()
        pbsParam.jointMaxVelocity = 100
        pbsParam.jointMaxAcceleration = 200
        pbsParam.servoMaxVelocity = 100
        pbsParam.servoMaxAcceleration = 200
        pbsParam.linearMaxVelocity = 200
        pbsParam.linearMaxAcceleration = 500
        pbsParam.pauseTime = 100
        pbsParam.jumpHeight = 20
        dll.SetPlaybackStaticParams(byref(pbsParam))

        pbdParam = PlaybackDynamicParams()
        pbdParam.velocityRatio = 30
        pbdParam.accelerationRatio = 30
        dll.SetPlaybackDynamicParams(byref(pbdParam))
        
        dll.SetPlaybackAngleBufferCmd.argtypes = [POINTER(PlaybackAngleBufferCmd)]
        playbackAngleCmd = PlaybackAngleBufferCmd()
        playbackAngleCmd.motionStyle = 0
        playbackAngleCmd.isGrab = 0
        playbackAngleCmd.gripper = 0
        playbackAngleCmd.joint4 = 0
        for i in range(3):
            playbackAngleCmd.joint1 = 30+i*10
            playbackAngleCmd.joint2 = 30+i*10
            playbackAngleCmd.joint3 = 30+i*10
            playbackAngleCmd.joint4 = 30+i*10
            dll.SetPlaybackAngleBufferCmd(byref(playbackAngleCmd))
                
dll.DobotExec()
dll.DisconnectDobot()