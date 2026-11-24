from datetime import date
import pandas as pd
from database import get_connection

ATTENDANCE_LIMIT = 75


def get_alerts(student_id, attendance_limit=ATTENDANCE_LIMIT):
    alerts = []
    conn = get_connection()
    records = pd.read_sql_query(
        "SELECT subject, attendance FROM academic_records "
        "WHERE student_id = ? ORDER BY record_id",
        conn, params=(student_id,),
    )
    quiz = pd.read_sql_query(
        "SELECT subject, topic, score FROM quiz_attempts "
        "WHERE student_id = ? ORDER BY attempt_id",
        conn, params=(student_id,),
    )
    plan = pd.read_sql_query(
        "SELECT planned_date, status FROM study_plans WHERE student_id = ?",
        conn, params=(student_id,),
    )
    conn.close()

    if not records.empty:
        latest = records.drop_duplicates("subject", keep="last")
        for r in latest.itertuples():
            if r.attendance < attendance_limit:
                alerts.append((
                    "warning",
                    f"{r.subject}: attendance is {r.attendance:.0f}%, below {attendance_limit}%. "
                    "Try to attend the next few classes to bring it up.",
                ))

    if not quiz.empty:
        for (subject, topic), g in quiz.groupby(["subject", "topic"]):
            scores = g["score"].tolist()
            if len(scores) >= 2 and scores[-1] < scores[-2]:
                alerts.append((
                    "warning",
                    f"{subject} - {topic}: score dropped from {scores[-2]:.0f}% "
                    f"to {scores[-1]:.0f}%. Review your mistakes and retake the quiz.",
                ))

    if not plan.empty:
        today = date.today().isoformat()
        overdue = plan[(plan["planned_date"] < today) & (plan["status"] != "done")]
        if not overdue.empty:
            alerts.append((
                "info",
                f"{len(overdue)} study task(s) from earlier days are still pending. "
                "Finish them or regenerate your plan.",
            ))

    return alerts