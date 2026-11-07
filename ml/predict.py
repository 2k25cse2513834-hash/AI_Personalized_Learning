import joblib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
MODEL_PATH = ROOT / "models" / "performance_model.pkl"
METRICS_PATH = ROOT / "models" / "metrics.csv"
FEATURES = ["marks", "attendance", "assignment_score", "study_hours"]

_model = None


def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_score(marks, attendance, assignment_score, study_hours):
    row = pd.DataFrame(
        [[marks, attendance, assignment_score, study_hours]], columns=FEATURES
    )
    score = float(load_model().predict(row)[0])
    return max(0.0, min(100.0, score))


def get_category(score):
    if score < 50:
        return "Needs improvement"
    if score < 70:
        return "Moderate"
    return "Strong"


def load_metrics():
    return pd.read_csv(METRICS_PATH)