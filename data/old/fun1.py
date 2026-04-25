import pandas as pd


# Load datasets
diseases_df = pd.read_csv("data/diseases.csv")
drugs_df = pd.read_csv("data/drugs.csv")
links_df = pd.read_csv("data/disease_drug_links.csv")


def get_recommendations(disease_name, top_n=5):
 # Filter recommendations for the selected disease
 recommendations = links_df[links_df["disease_name"] == disease_name]

 # Merge with drug information
 recommendations = recommendations.merge(
  drugs_df,
  on="drug_name",
  how="left"
 )

 # Sort by final score descending
 recommendations = recommendations.sort_values(by="final_score", ascending=False)

 # Return top N rows
 return recommendations.head(top_n)


# Test the function
selected_disease = "SARS-CoV-2"
result = get_recommendations(selected_disease, top_n=7)

print(f"\n=== Top Recommendations for {selected_disease} ===")
print(result[[
 "drug_name",
 "drug_class",
 "mechanism_of_action",
 "toxicity_level",
 "species_suitability",
 "repurposing_potential",
 "evidence_level_x",
 "final_score"
]])
result.to_excel("recommendations_output.xlsx", index=False)