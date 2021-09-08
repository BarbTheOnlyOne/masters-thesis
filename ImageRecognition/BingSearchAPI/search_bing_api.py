from requests import exceptions
import argparse
import requests
import cv2
import os

# Construct an argument parser for easier use of parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="Search query to search Bing Image API for.")
ap.add_argument("-o", "--output", required=True, help="Path to output directory of searched images.")
args = vars(ap.parse_args())

# Next set API key with maximum number of results for each search as well as group size for request/results
API_KEY = "ENTER_API_HERE"  # API key is missing for obvious reasons
MAX_RESULTS = 250
GROUP_SIZE = 50

# Endpoint API URL
URL = "https://api.bing.microsoft.com/v7.0/images/search"

# While downloading the images from the web some exceptions can be raised either
# by Python or by the requests library, here is a list of them
EXCEPTIONS = set([IOError, FileNotFoundError, exceptions.RequestException,
                  exceptions.HTTPError, exceptions.ConnectionError, exceptions.Timeout])

# This is the part for intializing parameters and making the search.
# Store the search term in a var, then set the params and header
term = args["query"]
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": term, "license": "any", "safeSearch": "off", "imageType": "photo", "count": GROUP_SIZE, "offset": 0}

# This code is the search
print(f"[INFO] Searching the Bing API for {term}.")
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# Get the results from the search , with total number of estimated results returned by Bing API
results = search.json()
estimated_number_of_results = min(results["totalEstimatedMatches"], MAX_RESULTS)
print(f"[INFO] {estimated_number_of_results} total results for {term}.")

# Total number of images downloaded
total_downloaded = 0

# Loop through the estimated number of results in "GROUP_SIZE" groups
for offset in range(0, estimated_number_of_results, GROUP_SIZE):
    # Update the search params with the offset, the make the request to fetch the results
    print(f"[INFO] Making request for group {offset} - {offset + GROUP_SIZE} of {estimated_number_of_results}")
    params["offset"] = offset
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print(f"[INFO] saving images for group {offset} - {offset + GROUP_SIZE} of {estimated_number_of_results}")
    for i in results["value"]:
        # Try to download the image
        try:
            # Make a request to download the image
            print(f"[INFO] Fetching {i['contentUrl']}")
            r = requests.get(i["contentUrl"], timeout=30)

            # Build the path to the output image
            extension = i["contentUrl"][i["contentUrl"].rfind("."):]
            path = os.path.altsep.join([args["output"], f"{str(total_downloaded).zfill(8)}{extension}"])

            # Write the image to disk
            f = open(path, "wb")
            f.write(r.content)
            f.close()

        # Try to catch error that would thwart the download of image
        except Exception as e:
            # Check if the exceptions is in the earlier stated list
            if type(e) in EXCEPTIONS:
                print(f"[INFO] Skipping {i['contentUrl']}")
                continue

        # Try to load the image from disk
        image = cv2.imread(path)

        # If its 'None', the it was not properly loaded and thus should be ignored
        if image is None:
            print(f"[INFO] Deleting {path}")
            os.remove(path)
            continue

        # Update the counter
        total_downloaded += 1

print("[INFO] Image scraping done, exiting script.")
