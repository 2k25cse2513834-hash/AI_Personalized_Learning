import sqlite3
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection, init_db


def register_student(name, email, password, confirm, course, semester):
    name, email = name.strip(), email.strip().lower()
    if not name or not email or not password:
        return False, "Please fill all fields."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if password != confirm:
        return False, "Passwords do not match."

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO students (name, email, password_hash, course, semester) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, email, generate_password_hash(password), course, semester),
        )
        conn.commit()
        return True, "Registration successful. Please login."
    except sqlite3.IntegrityError:
        return False, "This email is already registered."
    finally:
        conn.close()


def login_student(email, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE email = ?", (email.strip().lower(),)
    ).fetchone()
    conn.close()
    if row and check_password_hash(row["password_hash"], password):
        return {"student_id": row["student_id"], "name": row["name"], "email": row["email"]}
    return None


def require_login():
    init_db()
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login first from the Home page.")
        st.stop()
    return user