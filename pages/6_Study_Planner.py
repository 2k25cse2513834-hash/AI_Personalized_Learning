import streamlit as st
from auth import require_login
from modules.study_planner import build_plan, save_plan, get_plan, set_done

st.set_page_config(page_title="Study Planner", layout="wide")
user = require_login()
st.title("Personalized Study Planner")

col1, col2 = st.columns(2)
daily_minutes = col1.slider("Daily study time (minutes)", 30, 240, 90, 15)
days = col2.slider("Plan length (days)", 1, 7, 3)

if st.button("Generate / regenerate plan"):
    tasks = build_plan(user["student_id"], daily_minutes, days)
    if not tasks:
        st.warning(
            "No plan could be made. Take a few quizzes first, "
            "or you may have no weak or moderate topics right now."
        )
    else:
        save_plan(user["student_id"], tasks)
        st.success(f"Plan created with {len(tasks)} tasks.")

plan = get_plan(user["student_id"])
if plan.empty:
    st.info("No study plan yet. Click the button above after taking quizzes.")
    st.stop()

done_count = int((plan["status"] == "done").sum())
st.progress(done_count / len(plan), text=f"Completed {done_count} of {len(plan)} tasks")

for day, group in plan.groupby("planned_date"):
    st.subheader(day)
    for row in group.itertuples():
        label = (
            f"{row.subject} - {row.topic}: {row.task} "
            f"({row.duration_min} min, {row.priority} priority)"
        )
        checked = st.checkbox(label, value=(row.status == "done"), key=f"task_{row.plan_id}")
        if checked != (row.status == "done"):
            set_done(row.plan_id, user["student_id"], checked)
            st.rerun()