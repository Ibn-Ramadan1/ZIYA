import pandas as pd


# Load datasets
diseases_df = pd.read_csv("data/diseases.csv")
drugs_df = pd.read_csv("data/drugs.csv")
links_df = pd.read_csv("data/disease_drug_links.csv")


def is_species_compatible(drug_species, disease_species):
 drug_species = str(drug_species).lower()
 disease_species = str(disease_species).lower()

 return (
  disease_species in drug_species
  or "multi-species" in drug_species
  or "multi species" in drug_species
 )


def get_recommendations(disease_name, top_n=5):
 # Get disease species
 disease_row = diseases_df[diseases_df["disease_name"] == disease_name]

 if disease_row.empty:
  print(f"Disease '{disease_name}' not found.")
  return pd.DataFrame()

 disease_species = disease_row.iloc[0]["species"]

 # Filter recommendations for the selected disease
 recommendations = links_df[links_df["disease_name"] == disease_name]

 # Merge with drug information
 recommendations = recommendations.merge(
  drugs_df,
  on="drug_name",
  how="left"
 )

 # Filter by species suitability
 recommendations = recommendations[
  recommendations["species_suitability"].apply(
   lambda x: is_species_compatible(x, disease_species)
  )
 ]

 # Sort by final score descending
 recommendations = recommendations.sort_values(by="final_score", ascending=False)

 return recommendations.head(top_n)


# Test the function
selected_disease = "Lumpy Skin Disease (LSD)"
result = get_recommendations(selected_disease, top_n=5)

print(f"\n=== Top Recommendations for {selected_disease} ===")
print(result[[
 "drug_name",
 "drug_class",
 "species_suitability",
 "toxicity_level",
 "repurposing_potential",
 "final_score"
]])