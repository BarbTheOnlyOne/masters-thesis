from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os


ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True, help="Path to the cascades file.")
ap.add_argument("-o", "--output", required=True, help="Path to the output directory.")
args = vars(ap.parse_args())

detector = cv2.CascadeClassifier(args["cascade"])

print("[INFO] Starting video stream ...")
vs = VideoStream(usePiCamera=True).start() # Raspi cam
time.sleep(2.0)
total = 0

while True:
    frame = vs.read()
    frame = imutils.resize(frame, (640, 480))

    rectangles = detector.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 
                                           scaleFactor=1.1, 
                                           minNeighbors=5, 
                                           minSize=(30, 30))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("k"):
        print("[INFO] Saving image...")
        p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5))])
        cv2.imwrite(p, frame)
        total += 1
        print("[INFO] Image was saved")

    elif key == ord("q"):
        break

print("[INFO] Cleaning up ...")
cv2.destroyAllWindows()
vs.stop()
