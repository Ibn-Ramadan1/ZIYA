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


def get_confidence_badge(confidence):
    if confidence == "High Confidence":
        return "🟢 High Confidence"
    elif confidence == "Moderate Confidence":
        return "🟡 Moderate Confidence"
    else:
        return "🟠 Exploratory Candidate"


def get_toxicity_badge(toxicity):
    if toxicity == "High":
        return "🔴 High"
    elif toxicity == "Medium":
        return "🟡 Medium"
    else:
        return "🟢 Low"


def get_recommendations(
    disease_name,
    top_n=5,
    min_score=0,
    allowed_toxicities=None,
    allowed_confidence_levels=None
):
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

    recommendations = recommendations[recommendations["final_score"] >= min_score]

    recommendations["explanation"] = recommendations.apply(generate_explanation, axis=1)
    recommendations["confidence_level"] = recommendations["final_score"].apply(get_confidence_level)

    if allowed_toxicities:
        recommendations = recommendations[
            recommendations["toxicity_level"].isin(allowed_toxicities)
        ]

    if allowed_confidence_levels:
        recommendations = recommendations[
            recommendations["confidence_level"].isin(allowed_confidence_levels)
        ]

    recommendations = recommendations.sort_values(by="final_score", ascending=False)

    return recommendations.head(top_n)


def get_disease_details(disease_name):
    disease_row = diseases_df[diseases_df["disease_name"] == disease_name]
    if disease_row.empty:
        return None
    return disease_row.iloc[0]


# Defaults
default_disease = diseases_df["disease_name"].tolist()[0]
default_top_n = 5
default_min_score = 60
default_toxicities = ["Low", "Medium", "High"]
default_confidence = ["High Confidence", "Moderate Confidence", "Exploratory Candidate"]


# Sidebar
st.sidebar.title("ZIYA")
st.sidebar.markdown("### Project Overview")
st.sidebar.write("AI-Based Veterinary Drug Repurposing Platform")
st.sidebar.write("Focused on zoonotic and emerging animal diseases.")

st.sidebar.markdown("### Filters")

if st.sidebar.button("Reset Filters"):
    st.session_state["selected_disease"] = default_disease
    st.session_state["top_n"] = default_top_n
    st.session_state["min_score"] = default_min_score
    st.session_state["allowed_toxicities"] = default_toxicities
    st.session_state["allowed_confidence_levels"] = default_confidence

selected_disease = st.sidebar.selectbox(
    "Select disease",
    diseases_df["disease_name"].tolist(),
    key="selected_disease"
)

top_n = st.sidebar.slider(
    "Number of recommendations",
    min_value=3,
    max_value=10,
    value=default_top_n,
    key="top_n"
)

min_score = st.sidebar.slider(
    "Minimum score",
    min_value=0,
    max_value=100,
    value=default_min_score,
    key="min_score"
)

allowed_toxicities = st.sidebar.multiselect(
    "Allowed toxicity levels",
    options=["Low", "Medium", "High"],
    default=default_toxicities,
    key="allowed_toxicities"
)

allowed_confidence_levels = st.sidebar.multiselect(
    "Allowed confidence levels",
    options=["High Confidence", "Moderate Confidence", "Exploratory Candidate"],
    default=default_confidence,
    key="allowed_confidence_levels"
)

st.sidebar.markdown("### Database Summary")
st.sidebar.write(f"Diseases: {len(diseases_df)}")
st.sidebar.write(f"Drug Candidates: {len(drugs_df)}")
st.sidebar.write(f"Disease-Drug Links: {len(links_df)}")


# Main page
st.title("ZIYA")
st.subheader("AI-Based Veterinary Drug Repurposing Platform for Zoonotic and Emerging Animal Diseases")

st.write(
    "This platform ranks repurposed drug candidates based on efficacy, safety, "
    "evidence, and species suitability."
)

# Top metrics
m1, m2, m3 = st.columns(3)
m1.metric("Supported Diseases", len(diseases_df))
m2.metric("Drug Candidates", len(drugs_df))
m3.metric("Knowledge Links", len(links_df))

# Disease details section
disease_info = get_disease_details(selected_disease)

if disease_info is not None:
    st.markdown("### Disease Profile")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Species:** {disease_info['species']}")
        st.write(f"**Pathogen Type:** {disease_info['pathogen_type']}")
        st.write(f"**Target System:** {disease_info['target_system']}")
        st.write(f"**Zoonotic Risk:** {disease_info['zoonotic_risk']}")

    with col2:
        st.write(f"**Key Symptoms:** {disease_info['key_symptoms']}")
        st.write(f"**Molecular Target:** {disease_info['molecular_target']}")

if st.button("Analyze"):
    result = get_recommendations(
        selected_disease,
        top_n=top_n,
        min_score=min_score,
        allowed_toxicities=allowed_toxicities,
        allowed_confidence_levels=allowed_confidence_levels
    )

    if result.empty:
        st.warning("No recommendations found for the selected filters.")
    else:
        st.success(f"Top recommendations for {selected_disease}")

        download_df = result[[
            "drug_name",
            "drug_class",
            "mechanism_of_action",
            "toxicity_level",
            "species_suitability",
            "repurposing_potential",
            "final_score",
            "confidence_level",
            "explanation"
        ]].copy()

        csv_data = download_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name=f"{selected_disease}_recommendations.csv",
            mime="text/csv"
        )

        for _, row in result.iterrows():
            with st.container():
                st.markdown("---")
                st.markdown(f"## {row['drug_name']}")

                c1, c2, c3 = st.columns(3)
                c1.metric("Final Score", row["final_score"])
                c2.write(f"**Confidence:** {get_confidence_badge(row['confidence_level'])}")
                c3.write(f"**Toxicity:** {get_toxicity_badge(row['toxicity_level'])}")

                st.write(f"**Drug Class:** {row['drug_class']}")
                st.write(f"**Mechanism of Action:** {row['mechanism_of_action']}")
                st.write(f"**Species Suitability:** {row['species_suitability']}")
                st.write(f"**Repurposing Potential:** {row['repurposing_potential']}")
                st.write(f"**Explanation:** {row['explanation']}")

# Academic sections
st.markdown("---")
st.markdown("## About ZIYA")
st.write(
    "ZIYA is a prototype AI-based veterinary drug repurposing platform designed to "
    "support prioritization of therapeutic candidates for zoonotic and emerging animal diseases."
)

st.markdown("## Limitations")
st.write("- The current version uses a limited curated dataset.")
st.write("- Recommendations are prioritization aids, not direct treatment prescriptions.")
st.write("- Experimental, clinical, and species-specific validation are still required.")
st.write("- The current prototype supports only a limited number of diseases and drug candidates.")

st.markdown("## Future Work")
st.write("- Expand the disease and drug database.")
st.write("- Add machine learning ranking models.")
st.write("- Integrate molecular descriptors and similarity analysis.")
st.write("- Add bilingual Arabic/English interface.")
st.write("- Enable report export and advanced visual analytics.")