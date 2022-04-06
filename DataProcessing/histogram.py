from turtle import color
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math


filepath = "RANDOM_FILE_PATH"

df = pd.read_csv(filepath)
distance_column = df["vzdálenost rozpoznání obličeje"]

column_mean = distance_column.mean()
standard_deviation = distance_column.std()

# Sturges rule: k = [1 + 3,32 × log(n)]
bin_number = round(1 + 3.32 * math.log10(120))
min_number = distance_column.min()
max_number = distance_column.max()
column_range = max_number - min_number
one_step = column_range / bin_number

# Create the ranges of bins
bin_list = []
for i in range(0, bin_number + 1):
    bin_list.append(min_number + i * one_step)

bin_list = [1.25, 1.50, 1.75, 2.0, 2.25, 2.50, 2.75, 3.0, 3.25, 3.5, 3.75, 4.00]

# Set the font
plt.rcParams["font.family"] = "Arial"

sns.histplot(distance_column, bins=bin_list, kde=True)

# Format for display
mean_formated = "{:.2f}".format(column_mean)
std_formated = "{:.2f}".format(standard_deviation)

plt.xlabel("Vzdálenost [m]", fontsize="xx-large")
plt.ylabel("Počet", fontsize="xx-large")
plt.xlim(1, 4.25)
plt.xticks(bin_list, rotation="vertical")
plt.ylim(0, 85)
plt.grid(axis='y', alpha=0.75)
plt.axvline(x=column_mean, color="red", label=f"Průměr = {mean_formated}", ymax=0.9)
plt.text(column_mean, 85*0.95,'Průměr', color="red", fontsize="large")
plt.axvline(x=column_mean - 3*standard_deviation, color="red", label=f"St. odch. = {std_formated}", ymax=0.5)
plt.text(column_mean - 3*standard_deviation, 85*0.5,'-3σ', color="red", fontsize="large")
plt.axvline(x=column_mean + 3*standard_deviation, color="red", ymax=0.5)
plt.text(column_mean + 3*standard_deviation - 0.1, 85*0.5,'+3σ', color="red", fontsize="large")
plt.legend(loc="upper left", fontsize="large")
plt.tight_layout()
plt.savefig("histogram_night_20Y.png", dpi=300)
plt.show()