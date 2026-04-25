import pandas as pd
# عدل الكود يطلعلك اول 5 ادوية بس

# Load datasets
diseases_df = pd.read_csv("data/diseases.csv")
drugs_df = pd.read_csv("data/drugs.csv")
links_df = pd.read_csv("data/disease_drug_links.csv")

# Select a disease to test
selected_disease = "Lumpy Skin Disease (LSD)"

# Filter recommendations for the selected disease
recommendations = links_df[links_df["disease_name"] == selected_disease]

# Sort by final score descending
recommendations = recommendations.sort_values(by="final_score", ascending=False)

# Show results
print(f"\n=== Top Drug Recommendations for {selected_disease} ===")
print(recommendations[[
"drug_name",
"target_match",
"predicted_efficacy",
"predicted_safety",
"evidence_level",
"literature_support",
"final_score"
]])
