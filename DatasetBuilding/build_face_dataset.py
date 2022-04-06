# Get all the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os


# Argument parser with desired arguments to be parsed
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True, help="Path to the cascades file.")
ap.add_argument("-o", "--output", required=True, help="Path to the output directory.")
args = vars(ap.parse_args())

# Load OpenCV's Haar cascade
detector = cv2.CascadeClassifier(args["cascade"])

# Start the video stream, sleep for warm up, initialize counter for taken pictures
print("[INFO] Starting video stream ...")
vs = VideoStream(src=0).start() # This one for USB cam
# vs = VideoStream(usePiCamera=True).start() # This one for Raspi cam
time.sleep(2.0)
total = 0

# Loop over the frames from the stream
while True:
    # Grab a frame, clone it (just in case), resize for a faster face detection
    frame = vs.read()
    original = frame.copy()
    frame = imutils.resize(frame, width=400)

    # Detect faces in the grayscale frame
    rectangles = detector.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 
                                           scaleFactor=1.1, 
                                           minNeighbors=5, 
                                           minSize=(30, 30))

    # Loop over the face detections and draw them on the frame
    for (x, y, w, h) in rectangles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If 'k' was pressed, write the original
    if key == ord("k"):
        print("[INFO] Saving image...")
        p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5))])
        cv2.imwrite(p, original)
        total += 1
        print("[INFO] Image was saved")

    # If 'q' was pressed, break
    elif key == ord("q"):
        break

# Print total and do clean up
print(f"[INFO] {total} face images stored.")
print("[INFO] Cleaning up ...")
cv2.destroyAllWindows()
vs.stop()
