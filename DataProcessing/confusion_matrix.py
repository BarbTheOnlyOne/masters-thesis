import argparse
import pandas as pd
import os


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to the directory with csv files.")
args = vars(ap.parse_args())

directory_path = args["directory"]

unknown_true_counter = 0
unknown_false_counter = 0

known_true_counter = 0
known_false_counter = 0

for filename in os.listdir(directory_path):
    fp = os.path.join(directory_path, filename)

    df = pd.read_csv(fp)
    df = df.iloc[:10, -2:]

    # print(df)

    striped_values = df['správná identifikace'].str.strip()
    

    if filename == "neznamy1.csv" or filename == "neznamy2.csv":
        if 'ano' in striped_values.values:
            unknown_true_counter += df["správná identifikace"].str.strip().value_counts()["ano"]

        if 'ne' in striped_values.values:
            unknown_false_counter += df["správná identifikace"].str.strip().value_counts()["ne"]
    else:
        if 'ano' in striped_values.values:
            true_test = df["správná identifikace"].str.strip().value_counts()["ano"]
            known_true_counter += df["správná identifikace"].str.strip().value_counts()["ano"]

        if 'ne' in striped_values.values:
            false_test = df["správná identifikace"].str.strip().value_counts()["ne"]
            known_false_counter += df["správná identifikace"].str.strip().value_counts()["ne"]

print(f"[KNOWN] True positive results: {known_true_counter} | False negative results: {known_false_counter}")
print(f"[UNKNOWN] True negative results: {unknown_true_counter} | False positive results: {unknown_false_counter}")

