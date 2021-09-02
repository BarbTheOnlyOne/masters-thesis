from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os


# Handling the arguments from command line
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=True, help="Path to input directory of faces and images.")
ap.add_argument("-e", "--encodings", required=True, help="Path to serialized database of facial encodings.")
ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="Face detection model to use: 'hog' or 'cnn'.")
args = vars(ap.parse_args())

# Set the path to the input images
print("[INFO] Quantifying faces.")
image_paths = list(paths.list_images(args["dataset"]))

# These lists contain face encodings and names of said faces
known_encodings = []
known_names = []

# Make loop through all the image paths and extract their names
for (i, image_path) in enumerate(image_paths):
    print(f"[INFO] Processing image ({i+1})/({len(image_paths)})")
    name = image_path.split(os.path.sep)[-2]

    # Load the image with OpenCV, convert is in order, since desired value is RGB (dlib expects RGB)
    cv_image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

    # Next detect coordinates of bounding boxes and use them to compute facial embeddings
    bounding_boxes = face_recognition.face_locations(rgb_image, model=args["detection-method"])
    encodings = face_recognition.face_encodings(rgb_image, bounding_boxes)

    # Loop through the encoding and add it to earlier initialized lists
    for encoding in encodings:
        known_encodings.append(encoding)
        known_names.append(name)

# Dump the encodings with names into memory using pickle
print("[INFO] Serializing encodings with images.")
data = {"encodings": known_encodings, "names": known_names}
f = open(args["encodings"], "wb")  # 'wb' = write in binary
f.write(pickle.dumps(data))
f.close()
