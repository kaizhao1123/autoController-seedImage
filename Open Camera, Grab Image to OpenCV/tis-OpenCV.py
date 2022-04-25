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
import pathlib
import threading

lWidth = C.c_long()
lHeight = C.c_long()
iBitsPerPixel = C.c_int()
COLORFORMAT = C.c_int()


class camThread_1(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID

    def run(self):
        camera = FindCamera(self.camID)
        SetCamera(camera)
        ProcessLineContent(turn, int(imageCount), camera, self.camID)


class camThread_2(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID

    def run(self):
        currentCount = 0
        imageCount = 36
        camera = FindCamera(self.camID)
        SetCamera(camera)
        time.sleep(2)
        while currentCount < imageCount:
            CaptureImage(camera, currentCount + 1, id)
            time.sleep(2)
            currentCount += 1
        camera.StopLive()
        # cv2.destroyWindow('Window')


def FindCamera(id):
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # List availabe devices as uniqe names. This is a combination of camera name and serial number
    Devices = Camera.GetDevices()
    for i in range(len(Devices)):
        print(str(i) + " : " + str(Devices[i]))

    # Open a device with hard coded unique name:
    if id == 1:
        # Camera.open('DFK 37BUX287 15910406')  # for side cam
        Camera.open('DFK 37BUX287 15910398')  # for side cam
    else:
        Camera.open('DFK 37BUX287 15910400')  # for top cam

    print("OK")
    # or show the IC Imaging Control device page:

    # Camera.ShowDeviceSelectionDialog()

    return Camera


def SetCamera(camera):
    if camera.IsDevValid() == 1:
        # cv2.namedWindow('Window', cv2.cv.CV_WINDOW_NORMAL)
        print('Press ctrl-c to stop')

        # # Set a video format
        # camera.SetVideoFormat("RGB32 (640x480)")

        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate(30.0)

        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)

        # Set some properties
        # Exposure time

        ExposureAuto = [0]

        camera.GetPropertySwitch("Exposure", "Auto", ExposureAuto)
        print("Exposure auto : ", ExposureAuto[0])

        # In order to set a fixed exposure time, the Exposure Automatic must be disabled first.
        # Using the IC Imaging Control VCD Property Inspector, we know, the item is "Exposure", the
        # element is "Auto" and the interface is "Switch". Therefore we use for disabling:
        camera.SetPropertySwitch("Exposure", "Auto", 0)  # 0
        # "0" is off, "1" is on.

        ExposureTime = [0]
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs: ", ExposureTime[0])

        # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
        camera.SetPropertyAbsoluteValue("Exposure", "Value", 0.0303)  #################0.005

        # # Proceed with Gain, since we have gain automatic, disable first. Then set values.
        Gainauto = [0]
        camera.GetPropertySwitch("Gain", "Auto", Gainauto)
        print("Gain auto : ", Gainauto[0])

        camera.SetPropertySwitch("Gain", "Auto", 0)  # 0
        camera.SetPropertyValue("Gain", "Value", 0)

        WhiteBalanceAuto = [0]
        # Same goes with white balance. We make a complete red image:
        camera.SetPropertySwitch("WhiteBalance", "Auto", 1)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])

        camera.SetPropertySwitch("WhiteBalance", "Auto", 0)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])

        # camera.SetPropertyValue("WhiteBalance","White Balance Red",64)
        # camera.SetPropertyValue("WhiteBalance","White Balance Green",64)
        # camera.SetPropertyValue("WhiteBalance","White Balance Blue",64)
    else:
        print("No device selected")


def CaptureImage(camera, imgNumber, id):
    try:
        # Snap an image
        camera.SnapImage()
        # Get the image
        image = camera.GetImage()
        # Apply some OpenCV function on this image
        image = cv2.flip(image, 0)
        # cropped = image[0:380, 0:720]

        if id == 1:
            dic = './pic'
            cropped = image[0:272, 0:720]  # 265 341
        else:
            dic = './pic_t'
            cropped = image
        pathlib.Path(dic).mkdir(exist_ok=True)
        cv2.imwrite(dic + "/00{:02d}.bmp".format(imgNumber), cropped)

        if imgNumber < 37:
            seedId = '/5'

            times = '/pic10'
            if id == 1:
                saveDic = 'C:/Users/Kai Zhao/Desktop/image analysis/3d/Durum/55-lg-new/' + seedId + times
                # cropped = image[0:270, 0:720]
            else:
                saveDic = 'C:/Users/Kai Zhao/Desktop/paper/3d seed/images/two cam/wheat' + seedId + '/topview' + times
                cropped = image

            pathlib.Path(saveDic).mkdir(exist_ok=True)
            cv2.imwrite(saveDic + "/00{:02d}.bmp".format(imgNumber), cropped)
            cv2.imwrite('c:/Users/Kai Zhao/PycharmProjects/test/pic/' + ("%04d" % imgNumber) + '.bmp', cropped)

    except KeyboardInterrupt:
        camera.StopLive()
        cv2.destroyWindow('Window')


def SendGCode(connection, turn):
    print(turn)
    print(type(turn))
    connection.write((turn + '\n').encode('utf-8'))
    grbl_out = connection.readline()
    print(grbl_out.strip())


def ProcessLineContent(turn, imageCount, camera, id):
    currentCount = 0
    connection = serial.Serial('COM7', 115200)  # 6
    time.sleep(2)  # Wait for grbl to initialize
    connection.flushInput()  # Flush startup text in serial input

    while currentCount < imageCount:
        CaptureImage(camera, currentCount + 1, id)
        SendGCode(connection, turn)
        time.sleep(2)
        currentCount += 1

    connection.close()
    camera.StopLive()
    cv2.destroyAllWindows()
    # cv2.destroyWindow('Window')


def calculateFramePerSecond():
    video = cv2.VideoCapture(0)

    fps = video.get(cv2.CAP_PROP_FPS)


# 1st, control the motor to rotate over more than one round (540 degrees) and capture the videos.
# 2nd, deal with the video: Ignore the beginning part and the end part, leave the middle part of the video, which corresponds to precisely one round (360 degrees)
#      because there is acceleration when the motor starts to turn and slow down before it ends.
# 3rd, read and store the 36 frames (images) from the video.
def getImagesFromVideo():

    # open the camera, start to get the video
    videoCapture = cv2.VideoCapture(1)

    # set up the motor # 32/5 ; 39.5/4 ; 52.6/3 ; 79/2(best) ;
    turnDegrees = 540
    turn = 'G21G91G1X{}F79'.format((turnDegrees * 0.08884) / 10)
    connection = serial.Serial('COM7', 115200)  # 6
    time.sleep(2)  # Wait for grbl to initialize

    connection.flushInput()  # Flush startup text in serial input
    connection.write((turn + '\n').encode('utf-8'))
    grbl_out = connection.readline()
    connection.close()

    # store the images
    dic = './pic'
    i = 0
    j = 1
    while videoCapture.isOpened():

        success, frame = videoCapture.read()
        print()
        timeF = 2
        if i > timeF * 9 and i % timeF == 0:
            cv2.imwrite(dic + "/00{:02d}.bmp".format(j), frame)
            if j < 38:
                image = cv2.imread(dic + "/00{:02d}.bmp".format(j))
                crop = image[0:243, 0:720]
                cv2.imwrite(dic + "/00{:02d}.bmp".format(j), crop)
                cv2.imwrite('c:/Users/Kai Zhao/PycharmProjects/test/pic/' + ("%04d" % j) + '.bmp', crop)
                print("img output: %d" % j)
            j += 1
        i += 1
        if i > timeF * turnDegrees/10:
            break
    videoCapture.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    # argCount = len(sys.argv)
    # argCount = 2  ############################
    # if (argCount < 2):
    #     print("Image count is required.")
    #     exit()
    # else:
    #     # imageCount = sys.argv[1]
    #     imageCount = 38  ######################
    #
    # if (argCount > 3):
    #     print("No GCode for turn is provided. Defaulting to G21G91G1X0.088F51 which is 10 degrees.")
    #     turn = 'G21G91G1X0.088F51'
    # else:
    #     # turn degrees is converted to GCode units based on the assumption that 10 degrees is 0.088 in rotational units. A cross-multiplication is performed using the assumption
    #     # turnDegrees = int(sys.argv[2]    )
    #     turnDegrees = 10  ############################
    #     turn = 'G21G91G1X{}F51'.format((turnDegrees * 0.08884)/10)   # 0.088
    #
    #     # turn = 'G21G91G1X{}F51'.format((turnDegrees * 0.1775) / 10)  # 0.176 1775
    #     print(type(turn))
    #     print(turn)
    #
    # # camera1 = FindCamera("1")
    # # camera2 = FindCamera("2")
    # #
    # # SetCamera(camera1)
    # # SetCamera(camera2)
    # time.sleep(4)
    # # ProcessLineContent(turn, int(imageCount), camera)
    #
    # thread1 = camThread_1("Camera 1", 1)
    # # thread2 = camThread_2("Camera 2", 2)
    # thread1.start()
    # # thread2.start()

    ################################
    getImagesFromVideo()

    ############################
    # # test the camera
    #
    # vid = cv2.VideoCapture(1)
    #
    # while True:
    #
    #     # Capture the video frame
    #     # by frame
    #     ret, frame = vid.read()
    #
    #     # Display the resulting frame
    #     cv2.imshow('frame', frame)
    #
    #     # the 'q' button is set as the
    #     # quitting button you may use any
    #     # desired button of your choice
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    #
    # # After the loop release the cap object
    # vid.release()
    # # Destroy all the windows
    # cv2.destroyAllWindows()

