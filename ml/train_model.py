import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).parent.parent
FEATURES = ["marks", "attendance", "assignment_score", "study_hours"]

df = pd.read_csv(ROOT / "data" / "student_data.csv")
X = df[FEATURES]
y = df["next_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
}

results = []
best_name, best_model, best_mae = None, None, float("inf")

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    r2 = r2_score(y_test, pred)
    results.append({"model": name, "MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 3)})
    print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}")
    if mae < best_mae:
        best_name, best_model, best_mae = name, model, mae

models_dir = ROOT / "models"
models_dir.mkdir(exist_ok=True)
joblib.dump(best_model, models_dir / "performance_model.pkl")
pd.DataFrame(results).to_csv(models_dir / "metrics.csv", index=False)
print("Best model:", best_name)