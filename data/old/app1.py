import pandas as pd
import streamlit as st


# Page config
st.set_page_config(page_title="ZIYA", page_icon="🧬", layout="wide")


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


def generate_explanation(row):
    explanation = []

    if row["target_match"] == "High":
        explanation.append("strong target match")
    elif row["target_match"] == "Medium":
        explanation.append("moderate target match")

    if row["predicted_efficacy"] == "High":
        explanation.append("high predicted efficacy")
    elif row["predicted_efficacy"] == "Medium":
        explanation.append("moderate predicted efficacy")

    if row["predicted_safety"] == "High":
        explanation.append("good predicted safety")
    elif row["predicted_safety"] == "Medium":
        explanation.append("acceptable predicted safety")

    if row["literature_support"] == "High":
        explanation.append("strong literature support")
    elif row["literature_support"] == "Medium":
        explanation.append("some literature support")

    if row["repurposing_potential"] == "High":
        explanation.append("high repurposing potential")
    elif row["repurposing_potential"] == "Medium":
        explanation.append("moderate repurposing potential")

    if row["toxicity_level"] == "High":
        explanation.append("but toxicity risk is high")
    elif row["toxicity_level"] == "Medium":
        explanation.append("with moderate toxicity considerations")

    return ", ".join(explanation)


def get_confidence_level(score):
    if score >= 85:
        return "High Confidence"
    elif score >= 65:
        return "Moderate Confidence"
    else:
        return "Exploratory Candidate"


def get_recommendations(disease_name, top_n=5):
    disease_row = diseases_df[diseases_df["disease_name"] == disease_name]

    if disease_row.empty:
        return pd.DataFrame()

    disease_species = disease_row.iloc[0]["species"]

    recommendations = links_df[links_df["disease_name"] == disease_name]

    recommendations = recommendations.merge(
        drugs_df,
        on="drug_name",
        how="left"
    )

    recommendations = recommendations[
        recommendations["species_suitability"].apply(
            lambda x: is_species_compatible(x, disease_species)
        )
    ]

    recommendations = recommendations.sort_values(by="final_score", ascending=False)

    recommendations["explanation"] = recommendations.apply(generate_explanation, axis=1)
    recommendations["confidence_level"] = recommendations["final_score"].apply(get_confidence_level)

    return recommendations.head(top_n)


# UI
st.title("ZIYA")
st.subheader("AI-Based Veterinary Drug Repurposing Platform for Zoonotic and Emerging Animal Diseases")

st.write(
    "This platform ranks repurposed drug candidates based on efficacy, safety, evidence, "
    "and species suitability."
)

selected_disease = st.selectbox(
    "Select a disease",
    diseases_df["disease_name"].tolist()
)

top_n = st.slider("Number of recommendations", min_value=3, max_value=10, value=5)

if st.button("Analyze"):
    result = get_recommendations(selected_disease, top_n=top_n)

    if result.empty:
        st.warning("No recommendations found.")
    else:
        st.success(f"Top recommendations for {selected_disease}")

        for _, row in result.iterrows():
            with st.container():
                st.markdown("---")
                st.markdown(f"## {row['drug_name']}")
                st.write(f"**Drug Class:** {row['drug_class']}")
                st.write(f"**Mechanism of Action:** {row['mechanism_of_action']}")
                st.write(f"**Toxicity Level:** {row['toxicity_level']}")
                st.write(f"**Species Suitability:** {row['species_suitability']}")
                st.write(f"**Repurposing Potential:** {row['repurposing_potential']}")
                st.write(f"**Final Score:** {row['final_score']}")
                st.write(f"**Confidence Level:** {row['confidence_level']}")
                st.write(f"**Explanation:** {row['explanation']}")