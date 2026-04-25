from flask import Flask, render_template, request, send_file, Response
import io
import pandas as pd

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

app = Flask(__name__)

# Load data safely once at startup
try:
    diseases_df, drugs_df, links_df = load_data()
    DATA_ERROR = None
except Exception as e:
    diseases_df, drugs_df, links_df = None, None, None
    DATA_ERROR = str(e)


@app.route("/", methods=["GET", "POST"])
def index():
    if DATA_ERROR:
        return render_template(
            "index.html",
            project_name=PROJECT_NAME,
            project_subtitle=PROJECT_SUBTITLE,
            data_error=DATA_ERROR,
            diseases=[],
            selected_disease="",
            top_n=DEFAULT_TOP_N,
            min_score=DEFAULT_MIN_SCORE,
            selected_toxicities=TOXICITY_OPTIONS,
            selected_confidence=CONFIDENCE_OPTIONS,
            toxicity_options=TOXICITY_OPTIONS,
            confidence_options=CONFIDENCE_OPTIONS,
            disease_info=None,
            results=[],
            about=PROJECT_ABOUT,
            limitations=LIMITATIONS,
            future_work=FUTURE_WORK,
            disease_count=0,
            drug_count=0,
            link_count=0,
        )

    diseases = diseases_df["disease_name"].tolist()
    default_disease = diseases[0] if diseases else ""

    selected_disease = default_disease
    top_n = DEFAULT_TOP_N
    min_score = DEFAULT_MIN_SCORE
    selected_toxicities = TOXICITY_OPTIONS.copy()
    selected_confidence = CONFIDENCE_OPTIONS.copy()
    results = []
    disease_info = get_disease_details(selected_disease, diseases_df) if selected_disease else None

    if request.method == "POST":
        selected_disease = request.form.get("selected_disease", default_disease)

        try:
            top_n = int(request.form.get("top_n", DEFAULT_TOP_N))
        except ValueError:
            top_n = DEFAULT_TOP_N

        try:
            min_score = int(request.form.get("min_score", DEFAULT_MIN_SCORE))
        except ValueError:
            min_score = DEFAULT_MIN_SCORE

        selected_toxicities = request.form.getlist("allowed_toxicities")
        selected_confidence = request.form.getlist("allowed_confidence_levels")

        if not selected_toxicities:
            selected_toxicities = []
        if not selected_confidence:
            selected_confidence = []

        disease_info = get_disease_details(selected_disease, diseases_df)

        result_df = get_recommendations(
            selected_disease,
            diseases_df,
            drugs_df,
            links_df,
            top_n=top_n,
            min_score=min_score,
            allowed_toxicities=selected_toxicities,
            allowed_confidence_levels=selected_confidence,
        )

        if not result_df.empty:
            results = result_df.to_dict(orient="records")

    return render_template(
        "index.html",
        project_name=PROJECT_NAME,
        project_subtitle=PROJECT_SUBTITLE,
        data_error=None,
        diseases=diseases,
        selected_disease=selected_disease,
        top_n=top_n,
        min_score=min_score,
        selected_toxicities=selected_toxicities,
        selected_confidence=selected_confidence,
        toxicity_options=TOXICITY_OPTIONS,
        confidence_options=CONFIDENCE_OPTIONS,
        disease_info=disease_info,
        results=results,
        about=PROJECT_ABOUT,
        limitations=LIMITATIONS,
        future_work=FUTURE_WORK,
        disease_count=len(diseases_df),
        drug_count=len(drugs_df),
        link_count=len(links_df),
    )


@app.route("/download", methods=["POST"])
def download():
    if DATA_ERROR:
        return Response("Data error", status=400)

    selected_disease = request.form.get("selected_disease", "")
    try:
        top_n = int(request.form.get("top_n", DEFAULT_TOP_N))
    except ValueError:
        top_n = DEFAULT_TOP_N

    try:
        min_score = int(request.form.get("min_score", DEFAULT_MIN_SCORE))
    except ValueError:
        min_score = DEFAULT_MIN_SCORE

    selected_toxicities = request.form.getlist("allowed_toxicities")
    selected_confidence = request.form.getlist("allowed_confidence_levels")

    result_df = get_recommendations(
        selected_disease,
        diseases_df,
        drugs_df,
        links_df,
        top_n=top_n,
        min_score=min_score,
        allowed_toxicities=selected_toxicities,
        allowed_confidence_levels=selected_confidence,
    )

    if result_df.empty:
        return Response("No results to download", status=400)

    download_df = result_df[[
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

    buffer = io.StringIO()
    download_df.to_csv(buffer, index=False)
    output = io.BytesIO(buffer.getvalue().encode("utf-8"))
    output.seek(0)

    safe_name = selected_disease.replace(" ", "_").replace("/", "_")
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{safe_name}_recommendations.csv"
    )


if __name__ == "__main__":
    app.run(debug=True)