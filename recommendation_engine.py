from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# =========================
# Data Cleaning
# =========================

def clean_text_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_dataframe(df):
    df = df.copy()
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].apply(clean_text_value)
    return df


def fill_missing_values(diseases_df, drugs_df, links_df):
    diseases_df = diseases_df.fillna("")
    drugs_df = drugs_df.fillna("")
    links_df = links_df.fillna("")
    return diseases_df, drugs_df, links_df


# =========================
# Required Columns
# =========================

REQUIRED_DISEASE_COLUMNS = {
    "disease_id",
    "disease_name",
    "species",
    "pathogen_type",
    "target_system",
    "zoonotic_risk",
    "key_symptoms",
    "molecular_target",
}

REQUIRED_DRUG_COLUMNS = {
    "drug_id",
    "drug_name",
    "drug_class",
    "mechanism_of_action",
    "primary_use",
    "toxicity_level",
    "species_suitability",
    "repurposing_potential",
    "evidence_level",
}

REQUIRED_LINK_COLUMNS = {
    "disease_name",
    "drug_name",
    "target_match",
    "predicted_efficacy",
    "predicted_safety",
    "evidence_level",
    "literature_support",
    "final_score",
}


ALLOWED_THREE_LEVEL_VALUES = {"Low", "Medium", "High"}


# =========================
# Validation
# =========================

def validate_required_columns(df, required_columns, df_name):
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"{df_name} is missing required columns: {sorted(missing_columns)}"
        )


def validate_name_links(diseases_df, drugs_df, links_df):
    missing_diseases = set(links_df["disease_name"]) - set(diseases_df["disease_name"])
    missing_drugs = set(links_df["drug_name"]) - set(drugs_df["drug_name"])

    if missing_diseases:
        raise ValueError(
            f"disease_drug_links.csv contains disease names not found in diseases.csv: {sorted(missing_diseases)}"
        )

    if missing_drugs:
        raise ValueError(
            f"disease_drug_links.csv contains drug names not found in drugs.csv: {sorted(missing_drugs)}"
        )


def validate_allowed_values(df, column_name, allowed_values, df_name):
    invalid_values = set(df[column_name]) - allowed_values - {""}
    if invalid_values:
        raise ValueError(
            f"{df_name} contains invalid values in '{column_name}': {sorted(invalid_values)}. "
            f"Allowed values are: {sorted(allowed_values)}"
        )


def validate_final_score(links_df):
    links_df["final_score"] = pd.to_numeric(links_df["final_score"], errors="raise")

    invalid_scores = links_df[
        (links_df["final_score"] < 0) | (links_df["final_score"] > 100)
    ]

    if not invalid_scores.empty:
        raise ValueError(
            "disease_drug_links.csv contains final_score values outside the allowed range 0-100."
        )


# =========================
# AI Decision Engine
# =========================

LEVEL_SCORE_MAP = {
    "High": 100,
    "Medium": 65,
    "Low": 30,
    "": 0,
}

TOXICITY_SAFETY_MAP = {
    "Low": 100,
    "Medium": 65,
    "High": 30,
    "": 0,
}

AI_SCORE_WEIGHTS = {
    "target_match": 0.25,
    "predicted_efficacy": 0.30,
    "predicted_safety": 0.20,
    "evidence_level": 0.15,
    "literature_support": 0.10,
}


def level_to_score(value):
    return LEVEL_SCORE_MAP.get(str(value).strip(), 0)


def toxicity_to_safety_score(value):
    return TOXICITY_SAFETY_MAP.get(str(value).strip(), 0)


def calculate_ai_final_score(row):
    """
    AI-inspired weighted prioritization score.

    This is not a trained ML model yet.
    It is a transparent AI-inspired decision-support engine that converts
    biological, pharmacological, and evidence-based criteria into a final score.
    """

    target_score = level_to_score(row.get("target_match", ""))
    efficacy_score = level_to_score(row.get("predicted_efficacy", ""))
    safety_score = level_to_score(row.get("predicted_safety", ""))
    evidence_score = level_to_score(row.get("evidence_level", ""))
    literature_score = level_to_score(row.get("literature_support", ""))

    final_score = (
        target_score * AI_SCORE_WEIGHTS["target_match"]
        + efficacy_score * AI_SCORE_WEIGHTS["predicted_efficacy"]
        + safety_score * AI_SCORE_WEIGHTS["predicted_safety"]
        + evidence_score * AI_SCORE_WEIGHTS["evidence_level"]
        + literature_score * AI_SCORE_WEIGHTS["literature_support"]
    )

    return round(final_score)


def generate_ai_score_breakdown(row):
    return (
        f"Target match: {row.get('target_match', '')}, "
        f"Predicted efficacy: {row.get('predicted_efficacy', '')}, "
        f"Predicted safety: {row.get('predicted_safety', '')}, "
        f"Evidence level: {row.get('evidence_level', '')}, "
        f"Literature support: {row.get('literature_support', '')}"
    )


def generate_ai_decision_summary(row):
    drug_name = row.get("drug_name", "This candidate")
    disease_name = row.get("disease_name", "the selected disease")
    score = row.get("final_score", "")

    return (
        f"{drug_name} was prioritized for {disease_name} using an AI-inspired "
        f"weighted decision engine. The final score of {score} was calculated from "
        f"target matching, predicted efficacy, predicted safety, evidence level, "
        f"and literature support."
    )


# =========================
# Data Loading
# =========================

def load_data():
    diseases_df = pd.read_csv(DATA_DIR / "diseases.csv")
    drugs_df = pd.read_csv(DATA_DIR / "drugs.csv")
    links_df = pd.read_csv(DATA_DIR / "disease_drug_links.csv")

    diseases_df, drugs_df, links_df = fill_missing_values(diseases_df, drugs_df, links_df)

    diseases_df = clean_dataframe(diseases_df)
    drugs_df = clean_dataframe(drugs_df)
    links_df = clean_dataframe(links_df)

    validate_required_columns(diseases_df, REQUIRED_DISEASE_COLUMNS, "diseases.csv")
    validate_required_columns(drugs_df, REQUIRED_DRUG_COLUMNS, "drugs.csv")
    validate_required_columns(links_df, REQUIRED_LINK_COLUMNS, "disease_drug_links.csv")

    validate_name_links(diseases_df, drugs_df, links_df)

    validate_allowed_values(drugs_df, "toxicity_level", ALLOWED_THREE_LEVEL_VALUES, "drugs.csv")
    validate_allowed_values(drugs_df, "evidence_level", ALLOWED_THREE_LEVEL_VALUES, "drugs.csv")

    validate_allowed_values(links_df, "target_match", ALLOWED_THREE_LEVEL_VALUES, "disease_drug_links.csv")
    validate_allowed_values(links_df, "predicted_efficacy", ALLOWED_THREE_LEVEL_VALUES, "disease_drug_links.csv")
    validate_allowed_values(links_df, "predicted_safety", ALLOWED_THREE_LEVEL_VALUES, "disease_drug_links.csv")
    validate_allowed_values(links_df, "evidence_level", ALLOWED_THREE_LEVEL_VALUES, "disease_drug_links.csv")
    validate_allowed_values(links_df, "literature_support", ALLOWED_THREE_LEVEL_VALUES, "disease_drug_links.csv")

    validate_final_score(links_df)

    # Keep the manually curated CSV score for reference.
    links_df["curated_score"] = links_df["final_score"]

    # AI Decision Engine recalculates final_score dynamically.
    links_df["final_score"] = links_df.apply(calculate_ai_final_score, axis=1)

    # Add AI score breakdown for transparency.
    links_df["ai_score_breakdown"] = links_df.apply(generate_ai_score_breakdown, axis=1)

    return diseases_df, drugs_df, links_df


# =========================
# Recommendation Logic
# =========================

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
    else:
        explanation.append("limited target match")

    if row["predicted_efficacy"] == "High":
        explanation.append("high predicted efficacy")
    elif row["predicted_efficacy"] == "Medium":
        explanation.append("moderate predicted efficacy")
    else:
        explanation.append("low predicted efficacy")

    if row["predicted_safety"] == "High":
        explanation.append("good predicted safety")
    elif row["predicted_safety"] == "Medium":
        explanation.append("acceptable predicted safety")
    else:
        explanation.append("limited predicted safety")

    if row["evidence_level"] == "High":
        explanation.append("high evidence level")
    elif row["evidence_level"] == "Medium":
        explanation.append("moderate evidence level")
    else:
        explanation.append("low evidence level")

    if row["literature_support"] == "High":
        explanation.append("strong literature support")
    elif row["literature_support"] == "Medium":
        explanation.append("some literature support")
    else:
        explanation.append("limited literature support")

    if row["repurposing_potential"] == "High":
        explanation.append("high repurposing potential")
    elif row["repurposing_potential"] == "Medium":
        explanation.append("moderate repurposing potential")

    if row["toxicity_level"] == "High":
        explanation.append("but toxicity risk is high")
    elif row["toxicity_level"] == "Medium":
        explanation.append("with moderate toxicity considerations")
    elif row["toxicity_level"] == "Low":
        explanation.append("with relatively favorable toxicity profile")

    return ", ".join(explanation)


def get_confidence_level(score):
    if score >= 85:
        return "High Confidence"
    elif score >= 65:
        return "Moderate Confidence"
    else:
        return "Exploratory Candidate"


def get_recommendations(
    disease_name,
    diseases_df,
    drugs_df,
    links_df,
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
    how="left",
    suffixes=("_link", "_drug")
)

    if "evidence_level_link" in recommendations.columns:
        recommendations["evidence_level"] = recommendations["evidence_level_link"]
    elif "evidence_level_drug" in recommendations.columns:
        recommendations["evidence_level"] = recommendations["evidence_level_drug"]
    

    recommendations = recommendations[
        recommendations["species_suitability"].apply(
            lambda x: is_species_compatible(x, disease_species)
        )
    ]

    recommendations = recommendations[recommendations["final_score"] >= min_score]

    recommendations["explanation"] = recommendations.apply(generate_explanation, axis=1)
    recommendations["confidence_level"] = recommendations["final_score"].apply(get_confidence_level)
    recommendations["ai_decision_summary"] = recommendations.apply(generate_ai_decision_summary, axis=1)

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


def get_disease_details(disease_name, diseases_df):
    disease_row = diseases_df[diseases_df["disease_name"] == disease_name]
    if disease_row.empty:
        return None
    return disease_row.iloc[0]