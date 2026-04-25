import pandas as pd

# Load datasets
diseases_df = pd.read_csv("data/diseases.csv")
drugs_df = pd.read_csv("data/drugs.csv")
links_df = pd.read_csv("data/disease_drug_links.csv")

# Select a disease to test
selected_disease = "SARS-CoV-2"

# Filter recommendations for the selected disease
recommendations = links_df[links_df["disease_name"] == selected_disease]

# Merge with drug information
recommendations = recommendations.merge(
 drugs_df,
 on="drug_name",
 how="left"
)

# Sort by final score descending
recommendations = recommendations.sort_values(by="final_score", ascending=False)

# Show selected columns
print(f"\n=== Top Drug Recommendations for {selected_disease} ===")
print(recommendations[[
 "drug_name",
 "drug_class",
 "mechanism_of_action",
 "toxicity_level",
 "species_suitability",
 "repurposing_potential",
 "evidence_level_x",
 "final_score"
]])
