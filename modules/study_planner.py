from datetime import date, timedelta
import pandas as pd
from database import get_connection
from modules.weak_topics import get_topic_scores, classify, WEAK_LIMIT, STRONG_LIMIT


def build_plan(student_id, daily_minutes, days, weak=WEAK_LIMIT, strong=STRONG_LIMIT):
    topics = get_topic_scores(student_id)
    if topics.empty:
        return []

    topics = topics.copy()
    topics["status"] = topics["latest"].apply(lambda s: classify(s, weak, strong))
    todo = topics[topics["status"] != "Strong"].sort_values("latest")
    if todo.empty:
        return []

    # Weaker topic = bigger weight = more study time
    weights = [max(10, 100 - s) for s in todo["latest"]]
    total_weight = sum(weights)

    tasks = []
    for d in range(days):
        day = (date.today() + timedelta(days=d)).isoformat()
        for (_, row), w in zip(todo.iterrows(), weights):
            minutes = max(10, int(round(daily_minutes * w / total_weight / 5) * 5))
            if d == 0:
                task = "Study notes and solved examples"
            elif d == days - 1 and days > 1:
                task = "Retake the quiz and review mistakes"
            else:
                task = "Solve practice questions"
            tasks.append({
                "subject": row["subject"],
                "topic": row["topic"],
                "planned_date": day,
                "duration_min": minutes,
                "priority": "High" if row["status"] == "Needs improvement" else "Medium",
                "task": task,
            })
    return tasks

def save_plan(student_id, tasks):
    conn = get_connection()

    # Jo (subject, topic, date) pehle se done hai, uska naya task mat banao
    done_rows = conn.execute(
        "SELECT subject, topic, planned_date FROM study_plans "
        "WHERE student_id = ? AND status = 'done'",
        (student_id,),
    ).fetchall()
    done_keys = {(r["subject"], r["topic"], r["planned_date"]) for r in done_rows}

    conn.execute(
        "DELETE FROM study_plans WHERE student_id = ? AND status = 'pending'",
        (student_id,),
    )

    new_tasks = [
        t for t in tasks
        if (t["subject"], t["topic"], t["planned_date"]) not in done_keys
    ]
    conn.executemany(
        "INSERT INTO study_plans "
        "(student_id, subject, topic, planned_date, duration_min, priority, task) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (student_id, t["subject"], t["topic"], t["planned_date"],
             t["duration_min"], t["priority"], t["task"])
            for t in new_tasks
        ],
    )
    conn.commit()
    conn.close()

def get_plan(student_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT plan_id, subject, topic, planned_date, duration_min, priority, task, status "
        "FROM study_plans WHERE student_id = ? ORDER BY planned_date, plan_id",
        conn,
        params=(student_id,),
    )
    conn.close()
    return df


def set_done(plan_id, student_id, done):
    conn = get_connection()
    conn.execute(
        "UPDATE study_plans SET status = ? WHERE plan_id = ? AND student_id = ?",
        ("done" if done else "pending", plan_id, student_id),
    )
    conn.commit()
    conn.close()