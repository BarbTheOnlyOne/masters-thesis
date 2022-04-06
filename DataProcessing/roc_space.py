import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


# Day and night values
tpr = [0.85, 0.94, 0.90]
fpr = [0.1, 0.05, 0.10]

tpr_n = [0.45, 0.51, 0.49]
fpr_n = [0.25, 0.10, 0.25]

plot_label1 = "Denní měření"
plot_label2 = "Noční měření"

points_labels = ["A", "B", "C"]

# fpr = [0.1, 0.15, 0.18, 0.15, 0.25]
# tpr = [0.60, 0.75, 0.85, 0.90, 0.89]

# fpr_n = [0.60, 0.65, 0.73, 0.80, 0.79]
# tpr_n = [0.47, 0.35, 0.42, 0.38, 0.45]

# plot_label1 = "Měření X"
# plot_label2 = "Měření Y"
# points_labels = [1, 2, 3, 4, 5]

x_line = [0, 1]
y_line = [0, 1]
tick_spacing = 0.1

plt.rcParams["font.family"] = "Arial"

sns.scatterplot(x=fpr, y=tpr, marker="s", color="green", label=plot_label1)
sns.scatterplot(x=fpr_n, y=tpr_n, marker="D", color="blue", label=plot_label2)
# Loop through the day data points 
for i, text_label in enumerate (points_labels):
    plt.text(fpr[i]+0.02, tpr[i]+0.02, text_label)

# Loop through the night data points
for i, text_label in enumerate (points_labels):
    plt.text(fpr_n[i]+0.02, tpr_n[i]+0.02, text_label)

plt.plot(x_line, y_line, "--", label="Náhodný odhad", color="red")

plt.ylim(0, 1.0)
plt.xlim(0, 1)
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
plt.xlabel("FPR")
plt.ylabel("TPR")

#box = plt.gca().get_position()
#plt.gca().set_position([box.x0, box.y0, box.width * 0.7, box.height])
#bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.
plt.legend(loc="best")
plt.tight_layout()
plt.savefig("roc_space.png", dpi=300)
plt.show()
