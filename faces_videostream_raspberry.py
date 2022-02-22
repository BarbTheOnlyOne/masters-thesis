# All the necessary imports of packages
from os import write
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
from numpy import cdouble
import send_email


# Construct the argument parses and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True, help="Path to the face cascades file.")
ap.add_argument("-e", "--encodings", required=True, help="Path to the serialized database of facial encodings.")
ap.add_argument("-s", "--display", type=int, required=True, help="If the captured image should be shown on the screen (0 = False, 1 = True).")
ap.add_argument("-o", "--output", type=str, required=True, help="Name of the output file only!")
args = vars(ap.parse_args())

# Intilize and load detectors, known faces etc.
print("[INFO] Loading encodings and detectors...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"]) # Face detector
hog = cv2.HOGDescriptor() # Persons detector
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
fourcc = cv2.VideoWriter_fourcc(*"MJPG") # video writer

# Intialize the video stream, sleep to let the camera sensor to warm up
print("[INFO] Starting the video stream...")
# vs = VideoStream(src=0).start() # This line is for USB cam
vs = VideoStream(usePiCamera=True).start() # This line is for Raspi cam
time.sleep(2.0)
# Start the FPS counter
fps = FPS().start()

# Counter for which image to detect, snippet numbers and also flag for writer
image_counter = 0
video_time_start = 0
snippet_number = 0
# Email realted variables
receiver = "YOUR_MAIL@gmail.com"
body = "Alert! The secured spaces has been compromised!"

# Initilize array for found names, as well as default name
names = []
name = "Unknown"

# Loop the frames from the video stream
while True:
    # Grab the frame from the threaded video stream, resize it to 500px (faster processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)

    # Convert the input frame from BGR to RGB(for face recognition) and to grayscale (for face detection)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect any person in the frame
    present_persons = hog.detectMultiScale(grayscale, winStride=(8,8) )
    # If person was detected, start recording / or reset timer
    if present_persons:
        video_time_start = time.time()
        full_snippet_name = args["output"] + f"_{snippet_number}" + ".avi"
        writer = cv2.VideoWriter(full_snippet_name, 
                            fourcc, 20, 
                            (680, 480), 
                            True)  

    # Detect faces in the greyscale frame
    rectangles = detector.detectMultiScale(grayscale, 
                                        scaleFactor=1.1, 
                                        minNeighbors=5, 
                                        minSize=(30, 30))

    # OpenCV returns boxes in format of (x, y, w, h), but (top, right, bottom, left) is needed
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rectangles]

    if image_counter == 0:
        names.clear()
        # Next make the embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)

        # Loop through the encodings
        for encoding in encodings:
            # Attempt to match faces in the input with known ones
            matches = face_recognition.compare_faces(data["encodings"], encoding)

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
            else:
                name = "Unknown"

            names.append(name)

    # Counter for face encodings check
    image_counter += 1
    if image_counter == 10:
        image_counter = 0

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
    
    # This makes sure, that the recording runs for 10 seconds at least
    if video_time_start != 0 and (time.time() - video_time_start) < 10:
        writer.write(frame) 
    else:
        send_email.send_mail(receiver, body, full_snippet_name)
        writer.release()
        snippet_number += 1

    # Show the image based on the arguments
    if args["display"] > 0:
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

if writer is not None:
    writer.release()