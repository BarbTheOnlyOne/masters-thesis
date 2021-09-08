import face_recognition
import argparse
import pickle
import cv2

# Make the argument parser again
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True, help="Path to serialized database of facial encodings.")
ap.add_argument("-i", "--image", required=True, help="Path to input image.")
ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="Face detection model to use: 'hog' or 'cnn'.")
args = vars(ap.parse_args())

# Load all known faces with names and input images as well
print("[INFO] Loading encodings.")
data = pickle.loads(open(args["encodings"]), "rb").read()
cv_image = cv2.imread(args["image"])
rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

# For each face detect the coordinates of their respective bounding boxes,
# then compute facial embeddings for each face in the input image
print("[INFO] Recognizing faces.")
bounding_boxes = face_recognition.face_locations(rgb_image, model=args["detection-method"])
encodings = face_recognition.face_encodings(rgb_image, bounding_boxes)

# Initialize the list of names for each face detected
names = []

# Loop through the encodings from input images and try to match each face in the input image
# with the encodings from our dataset which we loaded from pickle
for encoding in encodings:
    matches = face_recognition.compare_faces(data["encodings"], encoding)
    name = "Unknown"

    # Check for matches, first find all the indexes of all matched face,
    # then get total number of counts of recognition for each detected face
    # and write it to a dictionary
    if True in matches:
        matched_ids = [i for (i, b) in enumerate(matches) if b]
        counts = {}

        # Loop through the indexes and hold count for each recognized face
        for i in matched_ids:
            name = data["name"][i]
            counts[name] = counts.get(name, 0) + 1

        # Determine the recognized face based on the largest number of votes,
        # can result in a tie, if so, the first entry of dictionary will be selected
        name = max(counts, key=counts.get)

    # Update the list of names
    names.append(name)

# Loop over the recognized faces
for ((top, right, bottom, left), name) in zip(bounding_boxes, names):
    # Here draw the predicted boxes around the recognized faces
    cv2.rectangle(cv_image, (left, top), (right, bottom), (0, 255, 0), 2)
    y = top - 15 if top - 15 > 15 else top + 15
    cv2.putText(cv_image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

cv2.imshow("Image", cv_image)
cv2.waitKey(0)
