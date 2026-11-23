"""Flask application entry point for AI-Powered Smart City Intelligence."""
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file
from dotenv import load_dotenv
import pandas as pd
import analytics
import ai_helper
import data_manager
import report_generator

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.secret_key = __import__("os").getenv("FLASK_SECRET_KEY", "local-development-key-change-me")
_current_df = data_manager.load_sample_data()
_thresholds = {"traffic": 1500, "aqi": 150, "z_score": 2.0}


def current_metrics():
    return analytics.analyze_dataset(_current_df, _thresholds["traffic"], _thresholds["aqi"], _thresholds["z_score"])


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/dashboard")
def dashboard_api():
    metrics = current_metrics()
    return jsonify({"metrics": metrics, "ai_mode": "live" if ai_helper.live_ai_available() else "demo", "thresholds": _thresholds})


@app.get("/api/traffic")
def traffic_api():
    m = current_metrics()
    return jsonify({"locations": m["locations"], "days": m["days"], "matrix": m["traffic_matrix"], "averages": m["traffic"]["average_by_location"]})


@app.get("/api/air-quality")
def air_quality_api():
    m = current_metrics()
    return jsonify({"locations": m["locations"], "days": m["days"], "matrix": m["aqi_matrix"], "averages": m["aqi"]["average_by_location"]})


@app.get("/api/analytics")
def analytics_api():
    return jsonify(current_metrics())


@app.get("/api/predictions")
def predictions_api():
    return jsonify(current_metrics()["predictions"])


@app.post("/api/upload-dataset")
def upload_dataset():
    global _current_df
    if "file" not in request.files:
        return jsonify({"error": "Choose a CSV file to upload."}), 400
    try:
        candidate = data_manager.validate_dataset(request.files["file"])
        # Require a consistent set of day labels for each location.
        counts = candidate.groupby("location")["day"].nunique()
        if counts.nunique() != 1:
            raise ValueError("Every location must contain the same number of distinct days.")
        _current_df = candidate
        return jsonify({"message": "Dataset uploaded and validated successfully.", "metrics": current_metrics()})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/reset-dataset")
def reset_dataset():
    global _current_df
    _current_df = data_manager.load_sample_data()
    return jsonify({"message": "Original sample dataset restored.", "metrics": current_metrics()})


@app.post("/api/settings")
def settings_api():
    payload = request.get_json(silent=True) or {}
    try:
        traffic = float(payload.get("traffic_threshold", _thresholds["traffic"]))
        aqi = float(payload.get("aqi_threshold", _thresholds["aqi"]))
        z = float(payload.get("z_score", _thresholds["z_score"]))
        if min(traffic, aqi, z) < 0:
            raise ValueError
        _thresholds.update({"traffic": traffic, "aqi": aqi, "z_score": z})
        return jsonify({"message": "Threshold settings updated.", "metrics": current_metrics(), "thresholds": _thresholds})
    except (TypeError, ValueError):
        return jsonify({"error": "Thresholds must be valid non-negative numbers."}), 400


@app.post("/api/ai/analyze")
def ai_analyze():
    try:
        return jsonify(ai_helper.analyze(current_metrics()))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/api/ai/recommendations")
def ai_recommendations():
    try:
        return jsonify(ai_helper.recommendations(current_metrics()))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/api/ai/ask")
def ai_ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question or len(question) > 1000:
        return jsonify({"error": "Enter a question of 1 to 1000 characters."}), 400
    try:
        return jsonify(ai_helper.ask(question, current_metrics()))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/api/ai/explain")
def ai_explain():
    payload = request.get_json(silent=True) or {}
    subject = str(payload.get("subject", "dashboard overview")).strip()[:300]
    try:
        return jsonify(ai_helper.explain(subject, current_metrics()))
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/api/ai/generate-report")
def generate_report():
    try:
        m = current_metrics()
        analysis_result = ai_helper.analyze(m)
        recs = ai_helper.recommendations(m)
        path = report_generator.generate_pdf(m, analysis_result, recs)
        return send_file(path, as_attachment=True, download_name=path.name, mimetype="application/pdf")
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception:
        app.logger.exception("Report generation failed")
        return jsonify({"error": "The report could not be generated. Please try again."}), 500


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File is too large. Maximum upload size is 5 MB."}), 413


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "An unexpected server error occurred."}), 500


if __name__ == "__main__":
    app.run(debug=True)
