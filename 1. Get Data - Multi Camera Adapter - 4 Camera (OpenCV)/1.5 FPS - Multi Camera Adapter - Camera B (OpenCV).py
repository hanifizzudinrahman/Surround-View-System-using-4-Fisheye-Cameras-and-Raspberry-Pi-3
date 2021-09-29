import RPi.GPIO as gp
from datetime import datetime as dtm
import cv2
import time
import os

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
    startTime = time.time()
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
        captureCamera(2,startTime)     # Camera B
# =========================================================
# =============== [ M A I N - F U N C T I O N ] -  [R A S P B E R R Y  P I  3 ]

# =============== [ F U N C T I O N ]
#=========================================================      
def captureCamera(cam,startTime):
    global done
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
            # Rotate 180
            #img = cv2.rotate(img, cv2.ROTATE_180)
            # Calculate FPS
            FPS = calculateFPS(img,startTime)
            startTime = time.time()
            # Show
            cv2.imshow("CSI Camera " + str(cam), img)
            # This also acts as
            key = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if key == ord("q") or key == ord("d"):
                done = 1
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")
#=========================================================
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
# =============== [ F U N C T I O N ]

if __name__ == "__main__":
    main()

    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)



