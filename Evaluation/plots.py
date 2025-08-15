import glob
import os.path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ====== SELECT TEST TYPE HERE ======
test_type = "MRT"  # Change to "MRT" when needed
result_folder = f'../Results_{test_type}'
result_files = glob.glob(os.path.join(result_folder,'*.csv'))
if len(result_files) == 1:
    file_path = result_files[0]
else:
    print("Expected exactly one CSV file, found:", len(result_files))

# ====== Load Data ======
data = pd.read_csv(file_path)
data = data[data.iloc[:, 0] !=  'Subject Name']

# ====== Get Conditions ======
conditions = [col for col in data['Condition'].unique()]

# ====== Boxplot (same for DRT and MRT) ======
box_values = []
for condition in conditions:
    condition_data = data[data['Condition'] == condition]
    overall_accuracy = pd.to_numeric(condition_data['Overall Performance (%)'], errors='coerce').dropna().values
    box_values.append(overall_accuracy)

plot_name = f'Boxplot_{test_type}.png'
plot_path = os.path.join(result_folder,plot_name)
plt.figure(figsize=(10, 6))
plt.boxplot(box_values, labels=conditions, patch_artist=True)
plt.title(f'Box Plot of Overall Accuracy Across Conditions ({test_type})')
plt.xlabel('Conditions')
plt.ylabel('Overall Accuracy (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(plot_path)
plt.show()

# ====== Heatmap ======
if test_type == "DRT":
    features = [
        'Voicing Performance (%)', 'Nasality Performance (%)',
        'Sustension Performance (%)', 'Sibilation Performance (%)',
        'Graveness Performance (%)', 'Compactness Performance (%)'
    ]
else:  # MRT
    features = [
        'Initial Consonants Performance (%)',
        'Final Consonants Performance (%)'
    ]

heatmap_data = {
    condition: [
        pd.to_numeric(data[data['Condition'] == condition][feature], errors='coerce').mean()
        for feature in features
    ]
    for condition in conditions
}

# Convert percentages to decimal fractions for plotting
df_heatmap = pd.DataFrame(heatmap_data, index=features) / 100

plot_name = f'Heatmap_{test_type}.png'
plot_path = os.path.join(result_folder,plot_name)
plt.figure(figsize=(11, 10))
sns.heatmap(df_heatmap, annot=True, cmap="coolwarm", linewidths=.5, cbar_kws={'label': 'Accuracy'})
plt.xlabel('Conditions')
plt.ylabel('Distinctive Features')
plt.title(f'Accuracy Heatmap for Distinctive Features and Conditions ({test_type})')
plt.tight_layout()
plt.savefig(plot_path)
plt.show()
