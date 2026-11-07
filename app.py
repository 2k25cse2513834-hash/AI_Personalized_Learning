import streamlit as st
from database import init_db
from auth import register_student, login_student

st.set_page_config(page_title="AI Personalized Learning", layout="wide")
init_db()

if "user" not in st.session_state:
    st.session_state["user"] = None

user = st.session_state["user"]
st.title("AI-Driven Personalized Learning System")

if user:
    st.success(f"Logged in as {user['name']}.")
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()
else:
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            student = login_student(email, password)
            if student:
                st.session_state["user"] = student
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab_register:
        with st.form("register_form"):
            name = st.text_input("Full name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm password", type="password")
            course = st.text_input("Course", value="B.Tech CSE")
            semester = st.number_input("Semester", min_value=1, max_value=8, value=3)
            reg_submitted = st.form_submit_button("Register")
        if reg_submitted:
            ok, msg = register_student(name, reg_email, reg_pass, confirm, course, int(semester))
            if ok:
                st.success(msg)
            else:
                st.error(msg)