import streamlit as st
import plotly.express as px
from database import get_connection
from auth import require_login
from ml.predict import predict_score, get_category, load_metrics, MODEL_PATH
import pandas as pd

st.set_page_config(page_title="Performance Prediction", layout="wide")
user = require_login()
st.title("AI Performance Prediction")

if not MODEL_PATH.exists():
    st.error("Model not found. Run: python ml/train_model.py")
    st.stop()

conn = get_connection()
df = pd.read_sql_query(
    "SELECT subject, marks, attendance, assignment_score, study_hours "
    "FROM academic_records WHERE student_id = ? ORDER BY record_id",
    conn,
    params=(user["student_id"],),
)
conn.close()

if df.empty:
    st.info("Add your academic records first (Academic Records page).")
    st.stop()

latest = df.drop_duplicates("subject", keep="last").reset_index(drop=True)
subject = st.selectbox("Select subject", latest["subject"])
row = latest[latest["subject"] == subject].iloc[0]

st.subheader("Inputs used for prediction")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Previous marks", f"{row['marks']:.0f}")
c2.metric("Attendance", f"{row['attendance']:.0f}%")
c3.metric("Assignment score", f"{row['assignment_score']:.0f}")
c4.metric("Study hours/day", f"{row['study_hours']:.1f}")

st.subheader("What if you study more?")
hours = st.slider("Daily study hours", 0.0, 8.0, float(row["study_hours"]), 0.5)

score = predict_score(row["marks"], row["attendance"], row["assignment_score"], hours)
base = predict_score(row["marks"], row["attendance"], row["assignment_score"], row["study_hours"])

st.subheader("Estimated next exam score")
m1, m2 = st.columns(2)
m1.metric("Predicted score", f"{score:.1f} / 100", delta=f"{score - base:+.1f} vs current habits")
m2.metric("Performance level", get_category(score))
st.caption("This is an estimate from a machine learning model, not a guaranteed result.")

st.subheader("Model evaluation")
metrics = load_metrics()
best = metrics.loc[metrics["MAE"].idxmin(), "model"]
st.write(f"Selected model (lowest MAE): **{best}**")
st.dataframe(metrics)
fig = px.bar(metrics, x="model", y="MAE", title="Model comparison (lower MAE is better)")
st.plotly_chart(fig)
st.caption(
    "Models were trained on clearly labelled synthetic demonstration data. "
    "These metrics show the pipeline works; they do not prove accuracy on real students."
)