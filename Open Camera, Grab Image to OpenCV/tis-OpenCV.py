# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 09:46:46 2016

Sample for tisgrabber to OpenCV Sample 2

Open a camera by name
Set a video format hard coded (not recommended, but some peoples insist on this)
Set properties exposure, gain, whitebalance
"""
import ctypes as C
import tisgrabber as IC
import cv2
import numpy as np
import serial
import time
import sys

lWidth=C.c_long()
lHeight= C.c_long()
iBitsPerPixel=C.c_int()
COLORFORMAT=C.c_int()


def FindCamera():
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # List availabe devices as uniqe names. This is a combination of camera name and serial number
    Devices = Camera.GetDevices()
    for i in range(len( Devices )):
        print( str(i) + " : " + str(Devices[i]))

    # Open a device with hard coded unique name:
    Camera.open('DFK 37BUX287 15910406')  #for side cam

    #Camera.open('DFK 37BUX287 15910400')  # for top cam

    print("OK")
    # or show the IC Imaging Control device page:

    #Camera.ShowDeviceSelectionDialog()
    
    return Camera

def SetCamera(camera):
    if camera.IsDevValid() == 1:
        #cv2.namedWindow('Window', cv2.cv.CV_WINDOW_NORMAL)
        print( 'Press ctrl-c to stop' )

        # # Set a video format
        #camera.SetVideoFormat("RGB32 (640x480)")
        
        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate( 30.0 )
        
        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)    

        # Set some properties
        # Exposure time

        ExposureAuto=[0]
        
        camera.GetPropertySwitch("Exposure","Auto",ExposureAuto)
        print("Exposure auto : ", ExposureAuto[0])

        
        # In order to set a fixed exposure time, the Exposure Automatic must be disabled first.
        # Using the IC Imaging Control VCD Property Inspector, we know, the item is "Exposure", the
        # element is "Auto" and the interface is "Switch". Therefore we use for disabling:
        camera.SetPropertySwitch("Exposure","Auto",0)  #0
        # "0" is off, "1" is on.

        ExposureTime=[0]
        camera.GetPropertyAbsoluteValue("Exposure","Value",ExposureTime)
        print("Exposure time abs: ", ExposureTime[0])

        
        # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
        camera.SetPropertyAbsoluteValue("Exposure","Value",0.005)  #################0.005

        # # Proceed with Gain, since we have gain automatic, disable first. Then set values.
        Gainauto=[0]
        camera.GetPropertySwitch("Gain","Auto",Gainauto)
        print("Gain auto : ", Gainauto[0])
        
        camera.SetPropertySwitch("Gain","Auto",0)     #0
        camera.SetPropertyValue("Gain","Value",0)

        WhiteBalanceAuto=[0]
        # Same goes with white balance. We make a complete red image:
        camera.SetPropertySwitch("WhiteBalance","Auto",1)
        camera.GetPropertySwitch("WhiteBalance","Auto",WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])

        camera.SetPropertySwitch("WhiteBalance","Auto",0)
        camera.GetPropertySwitch("WhiteBalance","Auto",WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])
        
        #camera.SetPropertyValue("WhiteBalance","White Balance Red",64)
        #camera.SetPropertyValue("WhiteBalance","White Balance Green",64)
        #camera.SetPropertyValue("WhiteBalance","White Balance Blue",64)    
    else:
        print( "No device selected")
    
def CaptureImage(camera, imgNumber):
    try:
        # Snap an image
        camera.SnapImage()
        # Get the image
        image = camera.GetImage()
        # Apply some OpenCV function on this image
        image = cv2.flip(image,0)
        #image = cv2.erode(image,np.ones((11, 11)))
        #cv2.imwrite("./img_{}.jpg".format(imgNumber), image)
        cv2.imwrite("./00{:02d}.bmp".format(imgNumber), image)
        #cv2.imshow('Window', image)
        #cv2.waitKey(1000)
           
    except KeyboardInterrupt:
        camera.StopLive()    
        cv2.destroyWindow('Window')   

def SendGCode(connection, turn):   
    #print("Sending: " + turn)
    print(turn)
    print(type(turn))
    connection.write((turn + '\n').encode('utf-8'))
    grbl_out = connection.readline()
    print(grbl_out.strip())


def ProcessLineContent(turn, imageCount, camera):
    currentCount = 0
    connection = serial.Serial('COM6', 115200) #4
    time.sleep(2)   # Wait for grbl to initialize
    connection.flushInput()  # Flush startup text in serial input

    while(currentCount < imageCount):
        CaptureImage(camera, currentCount + 1)  
        SendGCode(connection, turn)
        time.sleep(2)  
        currentCount += 1
    
    connection.close()
    camera.StopLive()    
    cv2.destroyWindow('Window')       

if __name__ == "__main__":
    argCount = len(sys.argv)
    argCount = 2 ############################
    if(argCount < 2):
        print("Image count is required.")
        exit()
    else:
        #imageCount = sys.argv[1]
        imageCount = 36 ######################


    if(argCount > 3):
        print("No GCode for turn is provided. Defaulting to G21G91G1X0.088F51 which is 10 degrees.")
        turn = 'G21G91G1X0.088F51'
    else:
        # turn degrees is converted to GCode units based on the assumption that 10 degrees is 0.088 in rotational units. A cross-multiplication is performed using the assumption
        #turnDegrees = int(sys.argv[2]    )
        turnDegrees = 10 ############################
       # turn = 'G21G91G1X{}F51'.format((turnDegrees * 0.088)/10)

        turn = 'G21G91G1X{}F51'.format((turnDegrees * 0.176) / 10)
        print(type(turn))
        print(turn)
    camera = FindCamera()

    SetCamera(camera)
    time.sleep(4)
    ProcessLineContent(turn, int(imageCount), camera)
