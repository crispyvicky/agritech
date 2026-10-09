"""
Standalone plant-disease worker (Keras 3 + Torch).
Run with .venv_plant — never import TensorFlow here.
"""
import json
import os
import sys

os.environ["KERAS_BACKEND"] = "torch"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
import numpy as np
import keras

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_CANDIDATES = [
    os.path.join(ROOT, "models", "best_plantdoc_model.keras"),
    os.path.join(ROOT, "models", "plantdoc_optimized_v2.keras"),
    os.path.join(ROOT, "models", "plantdoc_optimized_ema.keras"),
    os.path.join(ROOT, "models", "plantdoc_optimized.keras"),
    os.path.join(ROOT, "models", "plantdoc_best.keras"),
]
CLASS_PATH = os.path.join(ROOT, "models", "plantdoc_class_names.json")

_model = None
_class_names = None

HEALTHY = {
    "Apple leaf", "Bell_pepper leaf", "Blueberry leaf", "Cherry leaf", "grape leaf",
    "Peach leaf", "Raspberry leaf", "Soyabean leaf", "Strawberry leaf", "Tomato leaf",
}


def get_model():
    global _model
    if _model is not None:
        return _model
    last = None
    for path in MODEL_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            _model = keras.saving.load_model(path)
            return _model
        except Exception as e:
            last = e
    raise RuntimeError(f"Could not load plant model: {last}")


def get_classes():
    global _class_names
    if _class_names is None:
        with open(CLASS_PATH, "r", encoding="utf-8") as f:
            _class_names = json.load(f)
    return _class_names


def predict(image_path: str) -> dict:
    model = get_model()
    class_names = get_classes()

    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Could not read image: {image_path}"}

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224)).astype("float32")
    batch = np.expand_dims(img, 0)

    probs = model.predict(batch, verbose=0)
    if hasattr(probs, "numpy"):
        probs = probs.numpy()
    probs = np.array(probs)[0]

    top_idx = np.argsort(probs)[::-1][:3]
    top = [
        {"class": class_names[i], "confidence": round(float(probs[i]), 4)}
        for i in top_idx
        if i < len(class_names)
    ]

    best = top[0]
    conf = best["confidence"]
    uncertain = conf < 0.45
    status = "HEALTHY" if best["class"] in HEALTHY else "DISEASED"
    if uncertain:
        status = "UNCERTAIN"

    return {
        "class": best["class"],
        "confidence": conf,
        "status": status,
        "uncertain": uncertain,
        "top_predictions": top,
        "engine": "keras3-torch",
        "message": (
            "Low confidence — use a clearer close-up leaf photo."
            if uncertain
            else None
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: plant_predict_worker.py <image_path>"}))
        sys.exit(1)
    try:
        result = predict(sys.argv[1])
    except Exception as e:
        result = {"error": str(e)}
    print(json.dumps(result))
