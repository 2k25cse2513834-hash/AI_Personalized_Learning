import pandas as pd
import plotly.express as px
import streamlit as st
from database import get_connection
from auth import require_login
from modules.study_planner import get_plan
from modules.weak_topics import get_topic_scores

st.set_page_config(page_title="Progress Reports", layout="wide")
user = require_login()
st.title("Progress and Reports")

conn = get_connection()
quiz = pd.read_sql_query(
    "SELECT subject, topic, score FROM quiz_attempts "
    "WHERE student_id = ? ORDER BY attempt_id",
    conn,
    params=(user["student_id"],),
)
records = pd.read_sql_query(
    "SELECT subject, marks, attendance, assignment_score, study_hours "
    "FROM academic_records WHERE student_id = ? ORDER BY record_id",
    conn,
    params=(user["student_id"],),
)
conn.close()
plan = get_plan(user["student_id"])

st.subheader("Quiz improvement over time")
if quiz.empty:
    st.info("No quiz attempts yet. Take a quiz first.")
else:
    quiz["label"] = quiz["subject"] + " - " + quiz["topic"]
    quiz["attempt"] = quiz.groupby("label").cumcount() + 1
    fig = px.line(
        quiz, x="attempt", y="score", color="label", markers=True,
        range_y=[0, 100], title="Quiz score by attempt (per topic)",
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig)
    if quiz["attempt"].max() == 1:
        st.caption("Take a quiz on the same topic again to see a line showing your improvement.")

st.subheader("Subject-wise comparison")
if records.empty:
    st.info("No academic records yet.")
else:
    latest = records.drop_duplicates("subject", keep="last")
    long = latest.melt(
        id_vars="subject",
        value_vars=["marks", "attendance", "assignment_score"],
        var_name="metric",
        value_name="value",
    )
    fig2 = px.bar(
        long, x="subject", y="value", color="metric",
        barmode="group", range_y=[0, 100],
        title="Marks, attendance and assignment score",
    )
    st.plotly_chart(fig2)

st.subheader("Study goals")
if plan.empty:
    st.info("No study plan yet.")
else:
    done = int((plan["status"] == "done").sum())
    st.progress(done / len(plan), text=f"{done} of {len(plan)} tasks completed")

st.subheader("Download report")
lines = [f"Progress report for {user['name']}", ""]
lines.append("Academic records (latest per subject):")
if records.empty:
    lines.append("  none")
else:
    lines.append(records.drop_duplicates("subject", keep="last").to_string(index=False))
lines.append("")
lines.append("Topic analysis (latest quiz scores):")
topics = get_topic_scores(user["student_id"])
if topics.empty:
    lines.append("  none")
else:
    lines.append(topics.round(0).to_string(index=False))
lines.append("")
if not plan.empty:
    done_count = int((plan["status"] == "done").sum())
    lines.append(f"Study plan: {done_count} of {len(plan)} tasks completed")
lines.append("")
lines.append("Note: predictions are estimates, not guaranteed results.")
report_text = "\n".join(lines)

st.download_button("Download report (.txt)", report_text, file_name="progress_report.txt")