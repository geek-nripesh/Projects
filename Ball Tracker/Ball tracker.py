#packages used

from collections import deque
from imutils.video import VideoStream
import numpy
import argparse
import cv2
import imutils
import time
from tkinter import *
from tkinter.ttk import *




#File title
window = Tk() 
window.title("Ball Tracker")

#Geometry
window.geometry('600x300')

#Label For file path
lbl = Label(window, text="Enter file path(Optional)")
lbl.grid(column=0, row=2)

#Text Field
vidpath = Entry(window, width=30)
vidpath.grid(column=1, row=2)

#Label for ball color
lbl = Label(window, text="Select Ball Color")
lbl.grid(column=0, row=3)


#radiobutton
selected = IntVar()
rad1 = Radiobutton(window,text='Black', value=1, variable=selected)
rad2 = Radiobutton(window,text='Green', value=2, variable=selected)
rad3 = Radiobutton(window,text='White', value=3, variable=selected)

rad1.grid(column=0, row=4)
rad2.grid(column=0, row=5)
rad3.grid(column=0, row=6)


#Define run button
def clicked(): 
    colorcode = selected.get()
    if colorcode == 1:
        colorUpper = (128,128,128)
        colorLower = (0,0,0)
    elif colorcode == 2:
        colorUpper = (70,255,255)
        colorLower = (40,40,40)
    elif colorcode == 3:
        colorUpper = (180,128,255)
        colorLower = (0,0,230)
    print(str(colorLower)+"\n"+str(colorUpper))
    print("File path is :"+vidpath.get() )

    
    #for argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", 
            help ="path to video file(optional)")
    ap.add_argument("-b", "--buffer", type=int, default=64, 
            help="max buffer size")
    args = vars(ap.parse_args())

    #list of tracked points
    pts= deque(maxlen=args["buffer"]) #initialise deque of pts. ,default is 64

    #if no video path provided move to webcam
    if not args.get("Video", False):
        vs = VideoStream(src=0).start()
    else:
        vs = cv2.VideoCapture(args["video"])

    #time for camera to start
    time.sleep(2.0)
    #looping time

    while True:
        frame = vs.read()
        frame = frame[1] if args.get("Video", False) else frame
        
        #if video is being played and video ends
        if frame is None:
            break

        #resize, blur, and convert frame to HSV
        frame = imutils.resize(frame, width=600) #downsizing helps in processing frames faster
        blurred = cv2.GaussianBlur(frame, (11, 11), 0) #reduce high freq noise, so we can focus on our object
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #convert frame to hsv color frame

        # To remove any blob by dilating it
        
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        #for outer boundry
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        if len(cnts)>0: #To check if there is atlest one contour
            c = max(cnts, key = cv2.contourArea) #Here we can change shape of boundry 
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c) #To find the different features of contours, like area, perimeter, centroid, bounding box etc
            center = (int (M["m10"] / M["m00"]), int (M["m01"] / M["m00"]))

            # Proceed only if object meets a specific size
            if radius > 10:
                #draw circle and centroid on frame and then update values
                cv2.circle(frame, (int (x), int (y)), int (radius), (223, 7, 255), 5)
                cv2.circle(frame, center, 20, (255, 255, 0), 3)
                
        #update the points queue
        pts.appendleft(center)

        #loop over set of tracked points
        for i in range(1, len(pts)):
            #if either of tracked points are none , ignore them  #if no object detected then it will be ignored
            if pts[i-1] is None or pts[i] is None:
                continue
            #compute thickness and draw connecting lines
            thickess= int(numpy.sqrt(args["buffer"] / float(i+1))* 2.5)
            cv2.line(frame, pts[i-1], pts[i], (3,273,70), thickess) #dimension and colour of tracing line
        
        #show frame on screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF  
        #stop if spacebar pressed
        if key == ord(" "):
            break
        # if not using video file then webcam stops
    if not args.get("video", False):
        vs.stop()
    #  other wise release camera 
    else:    
        vs.release()
        #close all windows
    cv2.destroyAllWindows()

#Button
strt = Button(window, text="Run Program", command=clicked)
strt.grid(column=1, row=0)




window.mainloop() 