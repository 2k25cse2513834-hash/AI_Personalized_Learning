import streamlit as st
from database import get_connection
from auth import require_login

st.set_page_config(page_title="My Profile", layout="wide")
user = require_login()
st.title("My Profile")


def ensure_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            student_id INTEGER PRIMARY KEY,
            college TEXT,
            goals TEXT,
            daily_minutes INTEGER DEFAULT 90,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    conn.commit()
    conn.close()


def load_profile(student_id):
    conn = get_connection()
    student = conn.execute(
        "SELECT name, email, course, semester FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    profile = conn.execute(
        "SELECT college, goals, daily_minutes FROM student_profiles WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    conn.close()
    return student, profile


ensure_table()

if st.session_state.pop("profile_saved", False):
    st.success("Profile saved.")

student, profile = load_profile(user["student_id"])

college_val = (profile["college"] or "") if profile else ""
goals_val = (profile["goals"] or "") if profile else ""
daily_val = int(profile["daily_minutes"] or 90) if profile else 90

with st.form("profile_form"):
    name = st.text_input("Full name", value=student["name"])
    st.text_input("Email", value=student["email"], disabled=True)
    course = st.text_input("Course", value=student["course"] or "")
    semester = st.number_input(
        "Semester", min_value=1, max_value=8, value=int(student["semester"] or 1)
    )
    college = st.text_input("College", value=college_val)
    goals = st.text_area("Learning goals", value=goals_val)
    daily = st.number_input(
        "Daily available study time (minutes)",
        min_value=15, max_value=480, value=daily_val, step=15,
    )
    saved = st.form_submit_button("Save profile")

if saved:
    if not name.strip():
        st.error("Name cannot be empty.")
    else:
        conn = get_connection()
        conn.execute(
            "UPDATE students SET name = ?, course = ?, semester = ? WHERE student_id = ?",
            (name.strip(), course.strip(), int(semester), user["student_id"]),
        )
        conn.execute(
            "INSERT INTO student_profiles (student_id, college, goals, daily_minutes) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(student_id) DO UPDATE SET "
            "college = excluded.college, goals = excluded.goals, "
            "daily_minutes = excluded.daily_minutes",
            (user["student_id"], college.strip(), goals.strip(), int(daily)),
        )
        conn.commit()
        conn.close()
        user["name"] = name.strip()
        st.session_state["profile_saved"] = True
        st.rerun()

st.subheader("Saved profile")
if profile is None:
    st.info("No profile details saved yet. Fill the form above and click Save profile.")
else:
    st.write(f"**Name:** {student['name']}")
    st.write(f"**Email:** {student['email']}")
    st.write(f"**Course:** {student['course'] or '-'} (Semester {student['semester']})")
    st.write(f"**College:** {profile['college'] or '-'}")
    st.write(f"**Learning goals:** {profile['goals'] or '-'}")
    st.write(f"**Daily study time:** {profile['daily_minutes']} minutes")