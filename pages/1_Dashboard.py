import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection
from auth import require_login
from ml.predict import predict_score
from modules.weak_topics import get_topic_scores, WEAK_LIMIT
from modules.alerts import get_alerts

st.set_page_config(page_title="Dashboard", layout="wide")
user = require_login()
st.title(f"Welcome, {user['name']}")

conn = get_connection()
df = pd.read_sql_query(
    "SELECT subject, marks, attendance, assignment_score, study_hours "
    "FROM academic_records WHERE student_id = ?",
    conn,
    params=(user["student_id"],),
)
conn.close()

if df.empty:
    st.info("No academic records yet. Add sample data to test the dashboard.")
    if st.button("Add sample data"):
        sample = [
            ("OS", 75, 85, 70, 3),
            ("Java", 80, 90, 75, 2),
            ("TOC", 60, 80, 65, 2),
            ("Cybersecurity", 70, 75, 68, 1),
        ]
        conn = get_connection()
        conn.executemany(
            "INSERT INTO academic_records "
            "(student_id, subject, marks, attendance, assignment_score, study_hours) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(user["student_id"], *row) for row in sample],
        )
        conn.commit()
        conn.close()
        st.rerun()
    st.stop()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total subjects", df["subject"].nunique())
c2.metric("Average score", f"{df['marks'].mean():.0f}%")
c3.metric("Attendance", f"{df['attendance'].mean():.0f}%")
c4.metric("Study hours/day", f"{df['study_hours'].mean():.1f}")
try:
    preds = [
        predict_score(r.marks, r.attendance, r.assignment_score, r.study_hours)
        for r in df.itertuples()
    ]
    predicted_avg = f"{sum(preds) / len(preds):.0f}%"
except Exception:
    predicted_avg = "N/A"
c5.metric("Predicted score", predicted_avg)
topic_df = get_topic_scores(user["student_id"])
if topic_df.empty:
    weak_count = "-"
else:
    weak_count = int((topic_df["latest"] < WEAK_LIMIT).sum())
c6.metric("Weak topics", weak_count)

alerts = get_alerts(user["student_id"])
if alerts:
    st.subheader("Alerts")
    for level, msg in alerts:
        if level == "warning":
            st.warning(msg)
        else:
            st.info(msg)
fig = px.bar(df, x="subject", y="marks", title="Subject-wise marks", range_y=[0, 100])
st.plotly_chart(fig)