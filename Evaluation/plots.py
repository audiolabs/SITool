import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ====== SELECT TEST TYPE HERE ======
test_type = "MRT"  # Change to "DRT" as needed
file_path = "/si-tool-speech-intelligibility-toolkit-for-subjective-evaluation/Results_MRT/MRT TEST_subjectivePerformance.csv"

# ====== Load Data ======
data = pd.read_csv(file_path)

# ====== Get Conditions ======
conditions = sorted(
    [col for col in data['Condition'].unique() if col.startswith('condition')],
    key=lambda x: int(x.replace('condition', ''))
)

# ====== Boxplot (same for DRT and MRT) ======
box_values = []
for condition in conditions:
    condition_data = data[data['Condition'] == condition]
    overall_accuracy = pd.to_numeric(condition_data['Overall Performance (%)'], errors='coerce').dropna().values
    box_values.append(overall_accuracy)

plt.figure(figsize=(10, 6))
plt.boxplot(box_values, labels=conditions, patch_artist=True)
plt.title(f'Box Plot of Overall Accuracy Across Conditions ({test_type})')
plt.xlabel('Conditions')
plt.ylabel('Overall Accuracy (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'/si-tool-speech-intelligibility-toolkit-for-subjective-evaluation/Results_MRT/Boxplot_{test_type}.png')
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


df_heatmap = pd.DataFrame(heatmap_data, index=features) / 100

plt.figure(figsize=(11, 10))
sns.heatmap(df_heatmap, annot=True, cmap="coolwarm", linewidths=.5, cbar_kws={'label': 'Accuracy'})
plt.xlabel('Conditions')
plt.ylabel('Distinctive Features')
plt.title(f'Accuracy Heatmap for Distinctive Features and Conditions ({test_type})')
plt.tight_layout()
plt.savefig(f'/si-tool-speech-intelligibility-toolkit-for-subjective-evaluation/Results_MRT/Heatmap_{test_type}.png')
plt.show()
