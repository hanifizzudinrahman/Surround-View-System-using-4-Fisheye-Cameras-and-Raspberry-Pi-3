import RPi.GPIO as gp
from datetime import datetime as dtm
import cv2
import time
import os
import numpy as np

# =============== [ P A R A M E T E R ] - [ F U L L ]
#=========================================================
# Calibrate Fish Eye
DIM=(640, 480)
K=np.array([[183.40960550714848, 0.0, 317.9915709633227], [0.0, 183.27059290430077, 229.7739640549374], [0.0, 0.0, 1.0]])
D=np.array([[0.0643628313155956], [-0.014811743124422176], [-0.02257099687818543], [0.009516432693973089]])
# Bird's Eye View (BEV)
pathResultImages = r"Result_Images\\"
heightBEV = 706
widthBEV = 1040
# Camera Filename Images
Camera_Name = "Camera Bird's Eye View"
#  Matrix Camera -> BEV
MatrixB = np.zeros((3,3), np.float)
MatrixB[0:3] = [[-3.70282162e+00,  1.35447487e-01,  6.77917664e+02], [-2.42284350e+00, -3.40403340e-01,  5.08361784e+02], [-6.71155256e-03, 3.64932494e-04,  1.00000000e+00]]
print("=> MatrixB = ", MatrixB)
print("="*50)
print()
#  Coordinate Small Square [BEST] Inside
pointXMin = 450
pointXMax = 655
pointYMin = 249
pointYMax = 438
print("=> pointXMin = ", pointXMin)
print("=> pointXMax = ", pointXMax)
print("=> pointYMin = ", pointYMin)
print("=> pointYMax = ", pointYMax)
print("="*50)
print()
#=========================================================
# =============== [ P A R A M E T E R ] - [ F U L L ]

# =============== [ P I N O U T - R A S P B E R R Y  P I  3 ]
#=========================================================
gp.setwarnings(False)
gp.setmode(gp.BOARD)

gp.setup(7, gp.OUT)
gp.setup(11, gp.OUT)
gp.setup(12, gp.OUT)

gp.setup(15, gp.OUT)
gp.setup(16, gp.OUT)
gp.setup(21, gp.OUT)
gp.setup(22, gp.OUT)

gp.output(11, True)
gp.output(12, True)
gp.output(15, True)
gp.output(16, True)
gp.output(21, True)
gp.output(22, True)
#=========================================================
# =============== [ P I N O U T - R A S P B E R R Y  P I  3 ]

done = 0

# =============== [ M A I N - F U N C T I O N ] -  [R A S P B E R R Y  P I  3 ]
#=========================================================
def main():
    i = 1
    print("==> 1. Size BEV")
    print("Height: ", heightBEV)
    print("Width: ", widthBEV)
    print() 
    while True:
        if done == 1:
            print('F I N I S H')
            break
        print()
        print("Picture ", i)
        print("Start testing the Camera B")
        i2c = "i2cset -y 1 0x70 0x00 0x05"
        os.system(i2c)
        gp.output(7, True)
        gp.output(11, False)
        gp.output(12, True)
        captureCamera("B")     # Camera B
# =========================================================
# =============== [ M A I N - F U N C T I O N ] -  [R A S P B E R R Y  P I  3 ]

# =============== [ F U N C T I O N ] - [ F U L L ]
#=========================================================    
def captureCamera(cam):
    global done
    global trigger
    saat_ini = dtm.now() #tgl dan jam saat ini
    now = dtm.strftime(saat_ini, '%d-%b-%Y_%H:%M:%S') # tpye = string
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera " + str(cam), cv2.WINDOW_AUTOSIZE)   
        # Resolution
        # Default = 640x480
        # Raspberry Pi Camera v2 (8 megapixel): 3280 x 2464
        # video at 1080p30, 720p60, 640x480p90
        # width =  #1920 - 1280 - 640 - 320 - 160 - 80 - 40 [BEST = 3280]
        # height = #1080 - 720 - 480 - 240 - 120 - 60 - 30  [BEST = 2464]
        width = 640        
        height = 480        
        cap.set(3, width)
        cap.set(4, height)   
        # Window
        while cv2.getWindowProperty("CSI Camera " + str(cam), 0) >= 0:
            ret_val, img = cap.read()
            startTime = time.time()
            # Rotate 180
            #img = cv2.rotate(img, cv2.ROTATE_180)
            # Fish Eye Calibrated
            img = fishEyeCalibrated(img)
            # Read Camera & Rotate
            img = readCamera(img,cam, Camera_Name)
            # Show  BEV Result
            img = showBEV_Result(img,Camera_Name,MatrixB, widthBEV,heightBEV)
            # Remove Small Square [BEST] Inside - [ F U L L ]
            img = removeSmallSquareFull(cam, img, pointXMin,pointXMax,pointYMin,pointYMax)
            # Show Line to Divided and Removes
            img = showLineDividedRemove(cam,img,Camera_Name, heightBEV,widthBEV)
            # Read BEV Remove Camera & Crop
            _, imgRotate = cropBEVRemovaCamera(cam, img,Camera_Name)
            # Calculate FPS
            FPS = calculateFPS(imgRotate,startTime)
            # Show
            cv2.imshow("CSI Camera " + str(cam), imgRotate)
            # This also acts as
            key = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if key == ord("q"):
                done = 1
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")  
#=========================================================
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def fishEyeCalibrated(oriImg):
    h,w = oriImg.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(oriImg, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def readCamera(img,cameraName, Camera_Filename):
    if (cameraName == "A"):
        # Rotate A - No Rotate
        pass
    elif (cameraName == "B"):
        # Camera B - Rotate 90 COUNTERCLOCKWISE
        img = cv2.rotate(img, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif (cameraName == "C"):
        # Camera C - Rotate 90 CLOCKWISE
        img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
    elif (cameraName == "D"):
        # Camera D - Rotate 180 
        img = cv2.rotate(img, cv2.cv2.ROTATE_180)
    '''
    cv2.imshow(Camera_Filename, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return img
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def showBEV_Result(img,Camera_Filename,matrix, width,height):
    imgBEV = cv2.warpPerspective(img,matrix, (width,height))
    '''
    cv2.imshow("-BEV-" + Camera_Filename, imgBEV)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return imgBEV
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def removeSmallSquareFull(cameraName, imgBEVCamera, xMin,xMax,yMin,yMax):
    thickness = -1
    color = (0,0,0)
    if cameraName == "A":
        img = cv2.rectangle(imgBEVCamera, (0,yMin), (imgBEVCamera.shape[1],yMax), color, thickness)
    elif cameraName == "B":
        img = cv2.rectangle(imgBEVCamera, (xMin,0), (xMax,imgBEVCamera.shape[0]), color, thickness)
    elif cameraName == "C":
        img = cv2.rectangle(imgBEVCamera, (xMin,imgBEVCamera.shape[0]), (xMax,0), color, thickness)
    elif cameraName == "D":
        img = cv2.rectangle(imgBEVCamera, (imgBEVCamera.shape[1],yMin), (0,yMax), color, thickness)
    '''
    cv2.imshow("removeSmallSquareFull", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return img
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def showLineDividedRemove(cameraName,imgBEVCamera,BEV_Camera_Name, heightBEV,widthBEV):
    color = (0,0,255)
    thickness = 1
    # Divided Into 2 Parts
    halfHeight = int(heightBEV/2)
    halfWidth = int(widthBEV/2)
    if cameraName == "A" or cameraName == "D":
        imgBEVCamera = cv2.line(imgBEVCamera, (0,halfHeight), (widthBEV,halfHeight), color, thickness)
        if cameraName == "A":
            # Removes Buttom Parts
            imgBEVCamera = cv2.rectangle(imgBEVCamera, (0,halfHeight), (widthBEV,halfHeight*2), (0,0,0), -1)
        elif cameraName == "D":
            # Removes Top Parts
            imgBEVCamera = cv2.rectangle(imgBEVCamera, (0,0), (widthBEV,halfHeight), (0,0,0), -1)
    elif cameraName == "C" or cameraName == "B":
        imgBEVCamera = cv2.line(imgBEVCamera, (halfWidth,0), (halfWidth,heightBEV), color, thickness)
        if cameraName == "C":
            # Removes Left Parts
            imgBEVCamera = cv2.rectangle(imgBEVCamera, (0,0), (halfWidth,heightBEV), (0,0,0), -1)
        elif cameraName == "B":
            # Removes Right Parts
            imgBEVCamera = cv2.rectangle(imgBEVCamera, (halfWidth,0), (halfWidth*2,heightBEV), (0,0,0), -1)
    '''
    cv2.imshow("Remove Parts" + BEV_Camera_Name, imgBEVCamera)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return imgBEVCamera
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def cropBEVRemovaCamera(cameraName,img,BEVRemove_Camera_Name):
    height = img.shape[0]
    width = img.shape[1]
    if cameraName == "A":
        x = 0
        h = int(height/2)
        y = 0
        w = width
        img = img[y:y+h, x:x+w]
        imgRotate = img
    elif cameraName == "B":
        x = 0
        h = height
        y = 0
        w = int(width/2)
        img = img[y:y+h, x:x+w]
        # Rotate 
        imgRotate = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif cameraName == "C":
        x = int(width/2)
        h = height
        y = 0
        w = int(width/2)
        img = img[y:y+h, x:x+w]
        imgRotate = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif cameraName == "D":
        x = 0
        h = int(height/2)
        y = int(height/2)
        w = width
        img = img[y:y+h, x:x+w]
        imgRotate = cv2.rotate(img, cv2.ROTATE_180)
    '''
    cv2.imshow("-Crop-" + BEVRemove_Camera_Name, img)
    cv2.imshow("-Rotate-" + BEVRemove_Camera_Name, imgRotate)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return img, imgRotate
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def calculateFPS(img,startTime):
    # font which we will be using to display FPS
    font = cv2.FONT_HERSHEY_SIMPLEX
    endTime = time.time()
    fps = 1/(endTime - startTime)
    # converting the fps into 2 decimal pint
    fps = format(fps, ".2f")
    cv2.putText(img, fps, (0, 30), font, 1, (100, 255, 0), 3, cv2.LINE_AA)
    return fps
#=========================================================
# =============== [ F U N C T I O N ] - [ F U L L ]

if __name__ == "__main__":
    main()

    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)




