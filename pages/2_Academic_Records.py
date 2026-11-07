import streamlit as st
import pandas as pd
from database import get_connection
from auth import require_login

st.set_page_config(page_title="Academic Records", layout="wide")
user = require_login()
st.title("Academic Records")

with st.form("record_form", clear_on_submit=True):
    subject = st.text_input("Subject")
    col1, col2 = st.columns(2)
    marks = col1.number_input("Previous marks (0-100)", min_value=0.0, max_value=100.0, value=60.0)
    attendance = col2.number_input("Attendance % (0-100)", min_value=0.0, max_value=100.0, value=75.0)
    assignment = col1.number_input("Assignment score (0-100)", min_value=0.0, max_value=100.0, value=60.0)
    study_hours = col2.number_input("Daily study hours", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
    submitted = st.form_submit_button("Save record")

if submitted:
    if not subject.strip():
        st.error("Please enter a subject name.")
    else:
        conn = get_connection()
        conn.execute(
            "INSERT INTO academic_records "
            "(student_id, subject, marks, attendance, assignment_score, study_hours) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user["student_id"], subject.strip(), marks, attendance, assignment, study_hours),
        )
        conn.commit()
        conn.close()
        st.success("Record saved.")

conn = get_connection()
df = pd.read_sql_query(
    "SELECT record_id, subject, marks, attendance, assignment_score, study_hours "
    "FROM academic_records WHERE student_id = ? ORDER BY record_id",
    conn,
    params=(user["student_id"],),
)
conn.close()

st.subheader("Your records")
if df.empty:
    st.info("No records yet. Add your first subject above.")
else:
    st.dataframe(df.drop(columns=["record_id"]))

    st.subheader("Delete a record")
    options = {
        f"#{row.record_id} - {row.subject} (marks {row.marks:.0f})": int(row.record_id)
        for row in df.itertuples()
    }
    choice = st.selectbox("Select a record", list(options.keys()))
    if st.button("Delete selected record"):
        conn = get_connection()
        conn.execute(
            "DELETE FROM academic_records WHERE record_id = ? AND student_id = ?",
            (options[choice], user["student_id"]),
        )
        conn.commit()
        conn.close()
        st.rerun()