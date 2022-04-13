from imutils.video import VideoStream
import imutils
import argparse
import time
import cv2
import numpy as np
import os


ap = argparse.ArgumentParser()
ap.add_argument("-s", "--display", type=int, required=True, help="If the captured image should be shown on the screen (0 = False, 1 = True).")
ap.add_argument("-o", "--output", type=str, required=True, help="Name of the output file only!")
args = vars(ap.parse_args())

hog = cv2.HOGDescriptor() # Persons detector
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Start the video stream, sleep for warm up
print("[INFO] Starting video stream ...")
vs = VideoStream(usePiCamera=True).start() # Raspi cam
time.sleep(2.0)
image_number = 0

while True:
    frame = vs.read()
    frame = imutils.resize(frame, (640, 480))
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect person in the frame
    boxes = hog.detectMultiScale(grayscale, winStride=(8,8))

    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

    for (xA, yA, xB, yB) in boxes:
        # display the detected boxes in the colour picture
        cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

    cv2.imshow('frame',frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("k"):
        print("[INFO] Saving image...")
        p = os.path.sep.join([args["output"], "{}.png".format(str(image_number).zfill(5))])
        cv2.imwrite(p, frame)
        image_number += 1
        print("[INFO] Image was saved")

    elif key == ord("q"):
        break

print("[INFO] Cleaning up ...")
cv2.destroyAllWindows()
vs.stop()