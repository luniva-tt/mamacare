import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load dataset
df = pd.read_csv("pregnancy_symptom_dataset_sample.csv")

# Fill missing values with string "None"
df.fillna("None", inplace=True)

# Encode categorical features
categorical_cols = ['bleeding', 'pain', 'vomiting', 'temperature', 'urine_color', 'fetal_movement']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le
    print(f"{col} classes: {le.classes_}")  # Check for 'None'

# Encode target
target_encoder = LabelEncoder()
df['condition_label'] = target_encoder.fit_transform(df['condition_label'])

# Split data
X = df.drop("condition_label", axis=1)
y = df["condition_label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = DecisionTreeClassifier(max_depth=4)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

print(label_encoders["bleeding"].classes_)

# Save model and encoders
joblib.dump(model, "model/pregnancy_model.joblib")
joblib.dump(label_encoders, "model/label_encoders.joblib")
joblib.dump(target_encoder, "model/target_encoder.joblib")
print("✅ Model and encoders saved!")






































# import pandas as pd
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# import joblib

# # Load CSV
# df = pd.read_csv("pregnancy_symptom_dataset_sample.csv")

# # Encode categorical features
# categorical_cols = ['bleeding', 'pain', 'vomiting', 'temperature', 'urine_color', 'fetal_movement']
# label_encoders = {}
# for col in categorical_cols:
#     le = LabelEncoder()
#     df[col] = le.fit_transform(df[col])
#     label_encoders[col] = le

# # Encode target
# target_encoder = LabelEncoder()
# df['condition_label'] = target_encoder.fit_transform(df['condition_label'])

# # Train/test split
# X = df.drop("condition_label", axis=1)
# y = df["condition_label"]
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# # Train model
# model = DecisionTreeClassifier(max_depth=4)
# model.fit(X_train, y_train)
# print(label_encoders["bleeding"].classes_)

# # Save models locally
# joblib.dump(model, "model/pregnancy_model.joblib")
# joblib.dump(label_encoders, "model/label_encoders.joblib")
# joblib.dump(target_encoder, "model/target_encoder.joblib")
