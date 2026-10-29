"""Crop recommendation from soil nutrients and climate using the trained Random Forest."""
import logging
from pathlib import Path

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "crop_recommendation.pkl"

_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
        logger.info(f"Loaded crop recommender ({len(_bundle['model'].classes_)} crops)")
    return _bundle


def recommend_crop(features: dict, top_k: int = 3) -> dict:
    bundle = _load()
    model, names = bundle["model"], bundle["features"]
    row = pd.DataFrame([[float(features[n]) for n in names]], columns=names)
    probs = model.predict_proba(row)[0]
    ranked = sorted(zip(model.classes_, probs), key=lambda kv: -kv[1])[:top_k]
    top = [{"crop": str(c).title(), "confidence": round(float(p) * 100, 2)} for c, p in ranked]
    return {
        "status": "success",
        "crop": top[0]["crop"],
        "confidence": top[0]["confidence"],
        "top3": top,
    }
