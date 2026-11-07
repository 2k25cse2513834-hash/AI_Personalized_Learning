import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
n = 500

marks = np.clip(rng.normal(65, 15, n), 0, 100)
attendance = np.clip(rng.normal(78, 12, n), 40, 100)
assignment = np.clip(rng.normal(68, 14, n), 0, 100)
study_hours = np.clip(rng.normal(2.5, 1.2, n), 0, 8)

# Synthetic target: next exam score (demonstration data, not real students)
next_score = (
    0.55 * marks
    + 0.15 * attendance
    + 0.15 * assignment
    + 2.0 * study_hours
    - 8 * (attendance < 60)
    + rng.normal(0, 4, n)
)
next_score = np.clip(next_score, 0, 100)

df = pd.DataFrame({
    "marks": marks,
    "attendance": attendance,
    "assignment_score": assignment,
    "study_hours": study_hours,
    "next_score": next_score,
}).round(1)

out = Path(__file__).parent.parent / "data" / "student_data.csv"
out.parent.mkdir(exist_ok=True)
df.to_csv(out, index=False)
print("Saved", len(df), "rows to", out)