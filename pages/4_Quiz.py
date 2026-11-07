import json
import pandas as pd
import streamlit as st
from pathlib import Path
from database import get_connection
from auth import require_login

st.set_page_config(page_title="Quiz", layout="wide")
user = require_login()
st.title("Quiz and Assessment")

QUIZ_FILE = Path(__file__).parent.parent / "data" / "quiz_questions.json"
with open(QUIZ_FILE, encoding="utf-8") as f:
    quiz_data = json.load(f)

subject = st.selectbox("Subject", list(quiz_data.keys()))
topic = st.selectbox("Topic", list(quiz_data[subject].keys()))
questions = quiz_data[subject][topic]

with st.form(f"quiz_{subject}_{topic}"):
    answers = []
    for i, q in enumerate(questions):
        ans = st.radio(
            f"Q{i + 1}. {q['question']}",
            q["options"],
            index=None,
            key=f"{subject}_{topic}_{i}",
        )
        answers.append(ans)
    submitted = st.form_submit_button("Submit quiz")

if submitted:
    if any(a is None for a in answers):
        st.error("Please answer all questions before submitting.")
    else:
        correct = sum(
            1 for q, a in zip(questions, answers) if q["options"].index(a) == q["answer"]
        )
        total = len(questions)
        percent = correct / total * 100

        conn = get_connection()
        conn.execute(
            "INSERT INTO quiz_attempts (student_id, subject, topic, correct, total, score) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user["student_id"], subject, topic, correct, total, percent),
        )
        conn.commit()
        conn.close()

        st.success(f"Score: {correct}/{total} ({percent:.0f}%)")
        st.subheader("Review")
        for i, (q, a) in enumerate(zip(questions, answers)):
            right = q["options"][q["answer"]]
            if a == right:
                st.write(f"Q{i + 1}: Correct")
            else:
                st.write(f"Q{i + 1}: Your answer: {a}. Correct answer: {right}")
            st.caption(q["explanation"])

st.subheader("Your quiz history")
conn = get_connection()
hist = pd.read_sql_query(
    "SELECT subject, topic, correct, total, ROUND(score) AS score_percent, attempted_at "
    "FROM quiz_attempts WHERE student_id = ? ORDER BY attempt_id DESC LIMIT 10",
    conn,
    params=(user["student_id"],),
)
conn.close()
if hist.empty:
    st.info("No quiz attempts yet.")
else:
    st.dataframe(hist)