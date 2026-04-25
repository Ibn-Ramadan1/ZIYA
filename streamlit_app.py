import streamlit as st

from recommendation_engine import (
    load_data,
    get_recommendations,
    get_disease_details
)
from config import (
    PROJECT_NAME,
    PROJECT_SUBTITLE,
    DEFAULT_TOP_N,
    DEFAULT_MIN_SCORE,
    TOXICITY_OPTIONS,
    CONFIDENCE_OPTIONS,
    PROJECT_ABOUT,
    LIMITATIONS,
    FUTURE_WORK
)


# Page config
st.set_page_config(page_title=PROJECT_NAME, page_icon="🧬", layout="wide")

# Custom CSS
CUSTOM_CSS = """
<style>
.main {
    background-color: #f8fbff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.ziya-header {
    background: linear-gradient(90deg, #0f766e, #2563eb);
    padding: 1.2rem 1.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.2rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.ziya-subtext {
    font-size: 1rem;
    opacity: 0.95;
    margin-top: 0.4rem;
}

.ziya-section {
    background: white;
    padding: 1rem 1.2rem;
    border-radius: 14px;
    border: 1px solid #e5eefc;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}

.badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 0.75rem 0 1rem 0;
}

.badge {
    display: inline-block;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1;
    border: 1px solid transparent;
}

.badge-score {
    background-color: #dbeafe;
    color: #1d4ed8;
    border-color: #93c5fd;
}

.badge-confidence-high {
    background-color: #dcfce7;
    color: #166534;
    border-color: #86efac;
}

.badge-confidence-moderate {
    background-color: #fef3c7;
    color: #92400e;
    border-color: #fcd34d;
}

.badge-confidence-exploratory {
    background-color: #ffedd5;
    color: #9a3412;
    border-color: #fdba74;
}

.badge-toxicity-low {
    background-color: #dcfce7;
    color: #166534;
    border-color: #86efac;
}

.badge-toxicity-medium {
    background-color: #fef3c7;
    color: #92400e;
    border-color: #fcd34d;
}

.badge-toxicity-high {
    background-color: #fee2e2;
    color: #991b1b;
    border-color: #fca5a5;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def confidence_badge_html(confidence_level):
    if confidence_level == "High Confidence":
        return f'<span class="badge badge-confidence-high">🟢 {confidence_level}</span>'
    elif confidence_level == "Moderate Confidence":
        return f'<span class="badge badge-confidence-moderate">🟡 {confidence_level}</span>'
    else:
        return f'<span class="badge badge-confidence-exploratory">🟠 {confidence_level}</span>'


def toxicity_badge_html(toxicity_level):
    if toxicity_level == "High":
        return f'<span class="badge badge-toxicity-high">🔴 Toxicity: {toxicity_level}</span>'
    elif toxicity_level == "Medium":
        return f'<span class="badge badge-toxicity-medium">🟡 Toxicity: {toxicity_level}</span>'
    else:
        return f'<span class="badge badge-toxicity-low">🟢 Toxicity: {toxicity_level}</span>'


def score_badge_html(score):
    return f'<span class="badge badge-score">📊 Score: {score}</span>'


# Load datasets safely
try:
    diseases_df, drugs_df, links_df = load_data()
except Exception as e:
    st.error("Data loading/validation error")
    st.code(str(e))
    st.stop()

# Defaults
default_disease = diseases_df["disease_name"].tolist()[0]
default_top_n = DEFAULT_TOP_N
default_min_score = DEFAULT_MIN_SCORE
default_toxicities = TOXICITY_OPTIONS
default_confidence = CONFIDENCE_OPTIONS


# Sidebar
st.sidebar.title(PROJECT_NAME)
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
    options=TOXICITY_OPTIONS,
    default=default_toxicities,
    key="allowed_toxicities"
)

allowed_confidence_levels = st.sidebar.multiselect(
    "Allowed confidence levels",
    options=CONFIDENCE_OPTIONS,
    default=default_confidence,
    key="allowed_confidence_levels"
)

st.sidebar.markdown("### Database Summary")
st.sidebar.write(f"Diseases: {len(diseases_df)}")
st.sidebar.write(f"Drug Candidates: {len(drugs_df)}")
st.sidebar.write(f"Disease-Drug Links: {len(links_df)}")


# Main header
st.markdown(
    f"""
    <div class="ziya-header">
        <h1 style="margin:0;">{PROJECT_NAME}</h1>
        <div style="font-size:1.15rem; font-weight:600; margin-top:0.35rem;">
            {PROJECT_SUBTITLE}
        </div>
        <div class="ziya-subtext">
            This platform ranks repurposed drug candidates based on efficacy, safety, evidence, and species suitability.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Top metrics
m1, m2, m3 = st.columns(3)
m1.metric("Supported Diseases", len(diseases_df))
m2.metric("Drug Candidates", len(drugs_df))
m3.metric("Knowledge Links", len(links_df))

# Disease details section
disease_info = get_disease_details(selected_disease, diseases_df)

if disease_info is not None:
    st.markdown('<div class="ziya-section">', unsafe_allow_html=True)
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

    st.markdown("</div>", unsafe_allow_html=True)

if st.button("Analyze"):
    result = get_recommendations(
        selected_disease,
        diseases_df,
        drugs_df,
        links_df,
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

        st.markdown("### Recommended Drug Candidates")

        for _, row in result.iterrows():
            title = f"🧪 {row['drug_name']}"

            with st.expander(title, expanded=False):
                st.markdown(
                    f"""
                    <div class="badge-row">
                        {score_badge_html(row['final_score'])}
                        {confidence_badge_html(row['confidence_level'])}
                        {toxicity_badge_html(row['toxicity_level'])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(f"**Drug Class:** {row['drug_class']}")
                st.write(f"**Mechanism of Action:** {row['mechanism_of_action']}")
                st.write(f"**Species Suitability:** {row['species_suitability']}")
                st.write(f"**Repurposing Potential:** {row['repurposing_potential']}")
                st.write(f"**Explanation:** {row['explanation']}")

# Academic sections
st.markdown("---")

st.markdown('<div class="ziya-section">', unsafe_allow_html=True)
st.markdown("## About ZIYA")
st.write(PROJECT_ABOUT)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ziya-section">', unsafe_allow_html=True)
st.markdown("## Limitations")
for item in LIMITATIONS:
    st.write(f"- {item}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ziya-section">', unsafe_allow_html=True)
st.markdown("## Future Work")
for item in FUTURE_WORK:
    st.write(f"- {item}")
st.markdown("</div>", unsafe_allow_html=True)