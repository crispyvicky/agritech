"""Train the crop recommendation model (N, P, K, climate, pH, rainfall -> crop)."""
import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crop_recommendation.csv"
MODEL_PATH = ROOT / "models" / "crop_recommendation.pkl"
METRICS_PATH = ROOT / "models" / "crop_recommender_metrics.json"

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def main():
    df = pd.read_csv(DATA)
    X, y = df[FEATURES], df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    start = time.perf_counter()
    model.fit(X_train, y_train)
    train_seconds = time.perf_counter() - start

    preds = model.predict(X_test)
    metrics = {
        "samples": int(len(df)),
        "classes": int(y.nunique()),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "macro_f1": round(float(f1_score(y_test, preds, average="macro")), 4),
        "train_seconds": round(train_seconds, 3),
        "feature_importance": {
            f: round(float(v), 4)
            for f, v in sorted(
                zip(FEATURES, model.feature_importances_), key=lambda kv: -kv[1]
            )
        },
    }

    joblib.dump({"model": model, "features": FEATURES}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
