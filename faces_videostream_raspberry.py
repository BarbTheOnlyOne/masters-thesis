# All the necessary imports of packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
from numpy import cdouble


# Construct the argument parses and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True, help="Path to the face cascades file.")
ap.add_argument("-e", "--encodings", required=True, help="Path to the serialized database of facial encodings.")
args = vars(ap.parse_args())

# Load known faces with OpenCV's Haar cascade
print("[INFO] Loading encodings and Haar face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# Intialize the video stream, sleep to let the camera sensor to warm up
print("[INFO] Starting the video stream...")
# vs = VideoStream(src=0).start() # This line is for USB cam
vs = VideoStream(usePiCamera=True).start() # This line is for Raspi cam
time.sleep(2.0)

# Start the FPS counter
fps = FPS().start()

# Counter for which image to detect
image_counter = 0

# Loop the frames from the video stream
while True:

    # Grab the frame from the threaded video stream, resize it to 500px (faster processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    image_counter += 1

    # If the counter reached set amount, detect face
    if (image_counter == 5):
        # Don't forget to reset the counter, dummy
        image_counter = 0

        # Convert the input frame from BGR to RGB(for face recognition) and to grayscale (for face detection)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the greyscale frame
        rectangles = detector.detectMultiScale(grayscale, 
                                            scaleFactor=1.1, 
                                            minNeighbors=5, 
                                            minSize=(30, 30))

        # OpenCV returns boxes in format of (x, y, w, h), but (top, right, bottom, left) is needed
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rectangles]

        # Next make the embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # Loop through the encodings
        for encoding in encodings:
            # Attempt to match faces in the input with known ones
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # Check to see if match was found
            if True in matches:
                # Find indexes of all matched faces, initialize dictionary to count the number of votes for each face
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # Loop over the matched indexes and mantain a count for each recognized face 
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # Determine the recognized face with the largest number of votes
                name = max(counts, key=counts.get)

            names.append(name)
            


        # Loop through the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # Draw the predicted face name on the image
            cv2.rectangle(frame, 
                        (left, top), 
                        (right, bottom), 
                        (0, 255, 0), 
                        2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, 
                        name, 
                        (left, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.75, 
                        (0, 255, 0), 
                        2)

    # Display the image to screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If 'q' was pressed, break
    if key == ord("q"):
        break

    # Update the FPS counter
    fps.update()

# Stop the timer and display FPS info
fps.stop()
print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approximate FPS: {:.2f}".format(fps.fps()))

# Cleanup
cv2.destroyAllWindows()
vs.stop()