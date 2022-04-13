# All the necessary imports of packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2


# Construct the argument parses and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True, help="Path to the serialized databse of facial encodings")
ap.add_argument("-o", "--output", type=str, help="Path to the output video")
ap.add_argument("-y", "--display", type=int, default=1, help="Whether to display the output fram to screen or not")
ap.add_argument("-d", "--detection_method", type=str, default="cnn", help="Face detection model to use: 'hog' or 'cnn'")
args = vars(ap.parse_args())

# Load known encodings with their respective names
print("[INFO] Loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# Intialize the video stream and pointer to output video file, sleep to let the camera sensor to warm up
print("[INFO] Starting the video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)

# Loop the frames from the video stream
while True:
    # Grab the frame from the threaded video stream
    frame = vs.read()

    # Convert the input frame from BGR to RGB, resize it to width of 750px (for better speed)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = imutils.resize(frame, width=750)
    r = frame.shape[1] / float(rgb.shape[1])

    # Detect the coordinates(x, y) of bounding boxes for each face in the frame, compute their embedings
    boxes = face_recognition.face_locations(rgb, model=args["detection_method"])
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # Loop through the encodings
    for encoding in encodings:
        # Attempt to match faces in the input with known ones
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        # Check to see if we have found a match
        if True in matches:
            # Find indexes of all matched faces, initialize dictionary to count the number of votes for each face
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # Loop over the matched indexes and mantain a count for each recognized face 
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # Determine the recogniýzed face with the largest number of votes
            name = max(counts, key=counts.get)

        names.append(name)

    # Loop through the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # Rescale the face coordinates
        top = int(top * r)
        right = int(right * r)
        bottom = int(bottom * r)
        left = int(left * r)

        # Draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # If the writer is None *AND* it is supposed to write the output to the disk, initialize writer
    if writer is None and args["output"] is not None:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(args["output"], 
                                 fourcc, 20, 
                                 (frame.shape[1], frame.shape[0]), 
                                 True)
        
    # If the writer is not None, write the frame with recognized faces to disk
    if writer is not None:
        writer.write(frame)

    # Check to see if we are supposed to display the ouput frame to screen
    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # If the key "q" was pressed, break
        if key == ord("q"):
            break

# Cleanup
cv2.destroyAllWindows()
vs.stop()

if writer is not None:
    writer.release()