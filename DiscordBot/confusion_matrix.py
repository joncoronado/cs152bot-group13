from automation import classify_message
import pandas as pd
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
# Citation: We used AI to help generate code for creating a confusion matrix.

# # Load dataset
# dataset = pd.read_csv('../kaggle_parsed_dataset.csv')

# # Load context (if needed, or use empty list for each message)
# def load_context():
#     try:
#         with open('context.json') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []

# results = []
# for idx, row in tqdm(dataset.iterrows(), total=len(dataset)):
#     message = row['Text']
#     context = load_context()  # Or use [] if you want no context
#     try:
#         classification = classify_message(message, context)
#         # print(f'Harassment classification for message {idx}: {classification.harassment}')
#         # print(f'Reasoning: {classification.reasoning}')
#         results.append({
#             "index": row.get('index', idx),
#             "oh_label": row.get('oh_label', None),
#             "prediction": classification.harassment,
#             "tags": classification.tags,
#             "reasoning": classification.reasoning
#         })
#     except Exception as e:
#         results.append({
#             "index": row.get('index', idx),
#             "oh_label": row.get('oh_label', None),
#             "prediction": None,
#             "tags": None,
#             "reasoning": f"Error: {e}"
#         })

# results_df = pd.DataFrame(results)
# results_df.to_csv('harassment_predictions.csv', index=False)

# Load predictions (if not already loaded)
results_df = pd.read_csv('harassment_predictions.csv')

# Filter out rows with missing predictions or labels
filtered = results_df.dropna(subset=['prediction', 'oh_label'])

# Convert to integer labels (True/False to 1/0)
y_true = filtered['oh_label'].astype(int)
y_pred = filtered['prediction'].astype(int)

# Compute confusion matrix
cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Not Harassment", "Harassment"])

# Plot
fig, ax = plt.subplots(figsize=(6, 6))
disp.plot(ax=ax, cmap='Blues', values_format='d')
plt.title("Confusion Matrix: Harassment Prediction")
plt.show()

