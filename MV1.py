import time

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..', 'lib')))

##End of auto generated code##
import os, sys
from kbhit import KBHit
import colorama

import PFPyCameraLib as pf

import numpy as np
import cv2 as cv


def PromptEnterAndExit(code = 0):
    colorama.deinit()
    sys.exit(code)

def ExitWithErrorPrompt(errString, pfResult = None):
    print(errString)
    if pfResult is not None:
        print(pfResult)
    PromptEnterAndExit(-1)

def EventErrorCallback(cameraNumber, errorCode, errorMessage):
    print("[Communication error callback] Camera(",cameraNumber,") Error(", errorCode, ", ", errorMessage, ")\n")

def DiscoverAndSelectCamera():
    #Discover cameras in the network or connected to the USB port
    discovery = pf.PFDiscovery()
    pfResult = discovery.DiscoverCameras()

    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Discovery error:", pfResult)

    #Print all available cameras
    num_discovered_cameras = discovery.GetCameraCount()
    camera_info_list = []
    for x in range(num_discovered_cameras):
        [pfResult, camera_info] = discovery.GetCameraInfo(x)
        camera_info_list.append(camera_info) 
        print("[",x,"]")
        print(camera_info_list[x])

    #Prompt user to select a camera
    user_input = 0
    try:
        cam_id = int(user_input)
    except:
        ExitWithErrorPrompt("Error parsing input, not a number")

    #Check selected camera is within range
    if not 0 <= cam_id < num_discovered_cameras:
        ExitWithErrorPrompt("Selected camera out of range")

    selected_cam_info = camera_info_list[cam_id]
    #Call copy constructor
    #The camera info list elements are destroyed with PFDiscover
    if selected_cam_info.GetType() == pf.CameraType.CAMTYPE_GEV:
        copy_cam_info = pf.PFCameraInfoGEV(selected_cam_info)
    else:
        copy_cam_info = pf.PFCameraInfoU3V(selected_cam_info)

    return copy_cam_info


def ConnectAndConfigureCamera(pfCameraInfo):
    #Connect camera
    pfCam = pf.PFCamera()
    pfResult = pfCam.Connect(pfCameraInfo)

    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not connect to the selected camera", pfResult)

    #This sample assumes no DR
    #But to ensure it works with all cameras, we are going to disable DR
    [pfResult, featureList] = pfCam.GetFeatureList()
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not get feature list from camera", pfResult)

    #Check DoubleRate_Enable feature is present
    if any(elem.Name == "DoubleRate_Enable" for elem in featureList):
        print("DoubleRate_Enable feature found. Disabling feature.")
        pfResult = pfCam.SetFeatureBool("DoubleRate_Enable", False)
        if pfResult != pf.Error.NONE:
            ExitWithErrorPrompt("Failed to set DoubleRate_Enable", pfResult)

    #Set Mono8 pixel format
    pfResult = pfCam.SetFeatureEnum("PixelFormat", "Mono8")
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not set PixelFormat", pfResult)

    #Set Width to maximum
    pfResult, pfFeatureParam = pfCam.GetFeatureParams("Width")
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not get width feature parameters", pfResult)

    pfResult = pfCam.SetFeatureInt("Width", pfFeatureParam.Max)
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Error setting width", pfResult)

    #Set Height to maximum
    pfResult, pfFeatureParam = pfCam.GetFeatureParams("Height")
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not get Height feature parameters", pfResult)

    pfResult = pfCam.SetFeatureInt("Height", pfFeatureParam.Max)
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Error setting Height", pfResult)

    return pfCam

def SetupStream(pfCam, pfCamInfo):
    #Create stream depending on camera type
    if pfCamInfo.GetType() == pf.CameraType.CAMTYPE_GEV:
        pfStream = pf.PFStreamGEV(False, True, False, True)
    else:
        pfStream = pf.PFStreamU3V()
    #Set ring buffer size to 100
    pfStream.SetBufferCount(100)

    pfResult = pfCam.AddStream(pfStream)
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Error setting stream", pfResult)

    return pfStream



def DisplayFromStream(pfCam, pfStream):
    pfBuffer = 0
    pfImage = pf.PFImage()
    
    #Compute final image size (depending on DoubleRate being enabled)
    [_, width] = pfCam.GetFeatureInt("Width")
    [_, height] = pfCam.GetFeatureInt("Height")

    #print("Image W:%d H:%d" % (width, height))

    displaySize = (width,height)

    print("\nEntering grab loop...")


    #Fetch buffer
    [pfResult, pfBuffer] = pfStream.GetNextBuffer()
    if pfResult == pf.Error.NONE:
        #Get image object from buffer
        pfBuffer.GetImage(pfImage)

        #Do something with image data
        imageData = np.array(pfImage, copy = False)
        resizedImage = cv.resize(imageData, displaySize)
        cv.imwrite("MV1_"+str(time.time())+".png",resizedImage)



    #Release frame buffer, otherwise ring buffer will get full
    pfStream.ReleaseBuffer(pfBuffer)

    #Display stream statistics
    pfStreamStats = pfStream.GetStreamStatistics()


def GrabAndDisplay(pfCam, pfStream):
    #Start grabbing images into stream
    pfResult = pfCam.Grab()
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Could not start grab process", pfResult)

    #Get images from stream and display
    DisplayFromStream(pfCam, pfStream)

    #Stop frame grabbing
    pfResult = pfCam.Freeze()
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Error stopping grab process", pfResult)

def DisconnectCamera(pfCam):
    #Disconnect camera
    pfResult = pfCam.Disconnect()
    if pfResult != pf.Error.NONE:
        ExitWithErrorPrompt("Error disconnecting", pfResult)

if __name__ == "__main__":
    
    colorama.init()
    pf.SetEventErrorReceiver(EventErrorCallback)
    pfCamInfo = DiscoverAndSelectCamera()
    pfCam = ConnectAndConfigureCamera(pfCamInfo)
    pfStream = SetupStream(pfCam, pfCamInfo)
    
    GrabAndDisplay(pfCam, pfStream)
    
    DisconnectCamera(pfCam)

    PromptEnterAndExit()
