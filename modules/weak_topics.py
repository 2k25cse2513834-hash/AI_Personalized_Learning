import pandas as pd
from database import get_connection

WEAK_LIMIT = 50
STRONG_LIMIT = 75


def classify(score, weak=WEAK_LIMIT, strong=STRONG_LIMIT):
    if score < weak:
        return "Needs improvement"
    if score < strong:
        return "Moderate"
    return "Strong"


def get_topic_scores(student_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT subject, topic, score FROM quiz_attempts "
        "WHERE student_id = ? ORDER BY attempt_id",
        conn,
        params=(student_id,),
    )
    conn.close()
    if df.empty:
        return pd.DataFrame(
            columns=["subject", "topic", "attempts", "latest", "average", "trend"]
        )

    rows = []
    for (subject, topic), g in df.groupby(["subject", "topic"]):
        scores = g["score"].tolist()
        latest = scores[-1]
        if len(scores) > 1:
            diff = latest - scores[-2]
            trend = "Improving" if diff > 0 else "Declining" if diff < 0 else "Same"
        else:
            trend = "First attempt"
        rows.append({
            "subject": subject,
            "topic": topic,
            "attempts": len(scores),
            "latest": latest,
            "average": sum(scores) / len(scores),
            "trend": trend,
        })
    return pd.DataFrame(rows)