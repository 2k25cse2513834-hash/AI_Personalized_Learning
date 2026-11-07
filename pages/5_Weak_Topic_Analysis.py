import streamlit as st
import plotly.express as px
from auth import require_login
from modules.weak_topics import get_topic_scores, classify, WEAK_LIMIT, STRONG_LIMIT

st.set_page_config(page_title="Weak Topic Analysis", layout="wide")
user = require_login()
st.title("Weak Topic Analysis")

with st.expander("Thresholds (configurable)"):
    weak = st.number_input("Below this % = Needs improvement", 0, 100, WEAK_LIMIT)
    strong = st.number_input("At or above this % = Strong", 0, 100, STRONG_LIMIT)

if weak >= strong:
    st.error("The weak threshold must be lower than the strong threshold.")
    st.stop()

df = get_topic_scores(user["student_id"])
if df.empty:
    st.info("Take a quiz first (Quiz page) to see your topic analysis.")
    st.stop()

df["status"] = df["latest"].apply(lambda s: classify(s, weak, strong))
df["label"] = df["subject"] + " - " + df["topic"]
df = df.sort_values("latest")

fig = px.bar(
    df,
    x="label",
    y="latest",
    color="status",
    color_discrete_map={
        "Needs improvement": "#EF553B",
        "Moderate": "#FECB52",
        "Strong": "#00CC96",
    },
    range_y=[0, 100],
    title="Latest quiz score by topic (%)",
)
st.plotly_chart(fig)

st.subheader("Topic summary")
show = df[["subject", "topic", "attempts", "latest", "average", "trend", "status"]].copy()
show["latest"] = show["latest"].round(0)
show["average"] = show["average"].round(0)
st.dataframe(show)

st.subheader("Where to focus")
weak_df = df[df["status"] == "Needs improvement"]
if weak_df.empty:
    st.success("No weak topics right now. Keep revising and try harder quizzes.")
else:
    for r in weak_df.itertuples():
        st.warning(
            f"{r.label}: latest score {r.latest:.0f}% ({r.trend}). "
            "Revise this topic and retake the quiz."
        )