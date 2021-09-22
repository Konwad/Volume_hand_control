import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER                    
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#########################################
wCam, hCam = 1920, 1080      # resolution


cap = cv2.VideoCapture(0)       # turn on camera
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)     # object of the class form HandTrackingModule 


devices = AudioUtilities.GetSpeakers()          # from https://github.com/AndreMiras/pycaw
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()         # Range is equal (-74.0, 0.0, 0.03125)
minVol = volRange[0]            
maxVol = volRange[1]
vol = 0
#volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)                    # method from HandTrackingModule
    lmList = detector.findPosition(img, draw=False)  # method from HandTrackingModule
    if len(lmList) != 0:                             # checking if there are some points
        #print(lmList[4], lmList[8])                  # getting landmark of choosen number
        
        x1, y1 = lmList[4][1], lmList[4][2]          # first and second element (x,y coordinate)
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2              # coordinate of circle beetwen two points 
        
        cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)   # making sure that we are using correct numbers
        cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)   
        cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)         # making line beetween two points
        cv2.circle(img, (cx, cy), 15, (255,0,255), cv2.FILLED)  # making circle beetween two points on the line

        length = math.hypot(x2-x1, y2-y1)   # length beetwen points
        #print(length)

        # Hand range 50 - 300
        # Volume Range -74 - 0
        vol = np.interp(length, [50, 275], [minVol, maxVol])      # converting range beetwen two points volume.GetVolumeRange()  
        #volBar = np.interp(length, [50, 300], [400, 150])        # converting range again for showing volume bar correct
        volPer = np.interp(length, [50, 275], [0, 100])           # converting range again for showing percentage scale
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)                  # setting volume

        if length<50:
            cv2.circle(img, (cx, cy), 15, (0,255,0), cv2.FILLED)  # change color when length<50

    #cv2.rectangle(img, (50, 150), (85, 400), (0,255,0), 3)                  # creating bar that shows volume
    #cv2.rectangle(img, (50, int(vol)), (85, 400), (0,255,0), cv2.FILLED)     
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
 

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img,f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
