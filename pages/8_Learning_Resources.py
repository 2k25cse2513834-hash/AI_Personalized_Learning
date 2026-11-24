from urllib.parse import quote_plus
import streamlit as st
from auth import require_login
from modules.weak_topics import get_topic_scores, classify

st.set_page_config(page_title="Learning Resources", layout="wide")
user = require_login()
st.title("Learning Resources")

TIPS = {
    ("OS", "Processes"): [
        "Revise the process states and how a process moves between them.",
        "Learn what the Process Control Block stores.",
        "Practise scheduling: FCFS, SJF and Round Robin with small examples.",
    ],
    ("OS", "Memory"): [
        "Understand paging versus segmentation.",
        "Revise virtual memory and what causes a page fault.",
        "Practise page replacement problems step by step.",
    ],
    ("Java", "OOP"): [
        "Revise the four pillars: encapsulation, inheritance, polymorphism, abstraction.",
        "Know the difference between overloading and overriding.",
        "Revise access modifiers with a small example class.",
    ],
    ("Java", "Collections"): [
        "Compare List, Set and Map and when to use each.",
        "Know ArrayList versus LinkedList.",
        "Learn how HashMap stores key-value pairs.",
    ],
}
DEFAULT_TIPS = [
    "Re-read your class notes for this topic.",
    "Solve 5 practice questions, then retake the quiz.",
]

topics = get_topic_scores(user["student_id"])
if topics.empty:
    st.info("Take a quiz first to get resource recommendations.")
    st.stop()

topics["status"] = topics["latest"].apply(classify)
todo = topics[topics["status"] != "Strong"].sort_values("latest")
if todo.empty:
    st.success("No weak topics right now. Keep revising and try harder quizzes.")
    st.stop()

for r in todo.itertuples():
    with st.expander(f"{r.subject} - {r.topic} ({r.latest:.0f}%, {r.status})", expanded=True):
        st.write("Revision tips")
        for tip in TIPS.get((r.subject, r.topic), DEFAULT_TIPS):
            st.write(f"- {tip}")
        query = f"{r.subject} {r.topic}"
        c1, c2, c3 = st.columns(3)
        c1.link_button(
            "Video lessons",
            "https://www.youtube.com/results?search_query=" + quote_plus(query + " explained"),
        )
        c2.link_button(
            "Notes",
            "https://www.google.com/search?q=" + quote_plus(query + " notes"),
        )
        c3.link_button(
            "Practice questions",
            "https://www.google.com/search?q=" + quote_plus(query + " MCQ practice questions"),
        )

st.caption(
    "Resource buttons open a search for the topic. "
    "You can replace them with fixed links to your own course material."
)