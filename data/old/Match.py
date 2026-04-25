import pandas as pd

# Load datasets
diseases_df = pd.read_csv("data/diseases.csv")
drugs_df = pd.read_csv("data/drugs.csv")
links_df = pd.read_csv("data/disease_drug_links.csv")

# Cleaner
for df in [diseases_df, drugs_df, links_df]:
    df.columns = df.columns.str.strip() # تنظيف الهيدر
    # تنظيف أي عمود فيه نصوص من المسافات
    cols = df.select_dtypes(object).columns
    df[cols] = df[cols].apply(lambda x: x.str.strip())

# Show columns
print("=== Diseases Columns ===")
print(diseases_df.columns.tolist())

print("\n=== Drugs Columns ===")
print(drugs_df.columns.tolist())

print("\n=== Links Columns ===")
print(links_df.columns.tolist())

# Show unique disease names
print("\n=== Disease Names in diseases.csv ===")
print(diseases_df["disease_name"].unique())

print("\n=== Disease Names in disease_drug_links.csv ===")
print(links_df["disease_name"].unique())

# Show unique drug names
print("\n=== Drug Names in drugs.csv ===")
print(drugs_df["drug_name"].unique()[:10])

print("\n=== Drug Names in disease_drug_links.csv ===")
print(links_df["drug_name"].unique()[:10])

# Check missing disease names
missing_diseases = set(links_df["disease_name"]) - set(diseases_df["disease_name"])
print("\n=== Missing Diseases in diseases.csv ===")
print(missing_diseases)

# Check missing drug names
missing_drugs = set(links_df["drug_name"]) - set(drugs_df["drug_name"])
print("\n=== Missing Drugs in drugs.csv ===")
print(missing_drugs)