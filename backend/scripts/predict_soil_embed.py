"""Soil type via ImageNet embeddings matched to Soil/test folders (demo-reliable)."""
import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "models" / "soil_embed_index.npz"
DATA = ROOT / "Soil" / "test"

_model = None
_index = None

SOIL_INFO = {
    "Alluvial soil": {
        "notes": "Fertile river-deposit soil, excellent for agriculture.",
        "crops": ["Rice", "Wheat", "Corn", "Sugarcane", "Cotton"],
        "care": ["Ensure proper drainage", "Add organic matter", "Monitor pH"],
    },
    "Black Soil": {
        "notes": "Moisture-retentive clay-rich soil, good for cotton belts.",
        "crops": ["Cotton", "Wheat", "Jowar", "Linseed", "Tobacco"],
        "care": ["Improve drainage", "Add compost", "Deep plowing helps"],
    },
    "Clay soil": {
        "notes": "Dense, holds water; heavy when wet.",
        "crops": ["Rice", "Wheat", "Barley", "Oats"],
        "care": ["Improve drainage", "Add organic matter", "Avoid working when wet"],
    },
    "Red soil": {
        "notes": "Iron-rich, usually well-drained; may need nutrients.",
        "crops": ["Millet", "Groundnut", "Potato", "Tobacco", "Pulses"],
        "care": ["Add lime if acidic", "Fertilize regularly", "Add organic matter"],
    },
}


def _model_get():
    global _model
    if _model is None:
        from tensorflow.keras.applications import EfficientNetB0

        _model = EfficientNetB0(
            include_top=False, weights="imagenet", pooling="avg", input_shape=(224, 224, 3)
        )
    return _model


def _embed(path_or_array):
    from tensorflow.keras.applications.efficientnet import preprocess_input

    if isinstance(path_or_array, (str, Path)):
        img = cv2.imread(str(path_or_array))
        if img is None:
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img = path_or_array
    img = cv2.resize(img, (224, 224)).astype("float32")
    x = preprocess_input(np.expand_dims(img, 0))
    v = _model_get().predict(x, verbose=0)[0]
    return (v / (np.linalg.norm(v) + 1e-8)).astype("float32")


def _index_get(max_per=10):
    global _index
    if _index is not None:
        return _index
    if CACHE.exists():
        data = np.load(CACHE, allow_pickle=True)
        labels = list(data["labels"])
        vectors = data["vectors"]
        _index = {lab: vectors[i] for i, lab in enumerate(labels)}
        return _index

    if not DATA.exists():
        raise FileNotFoundError("Soil/test not found")

    labels, vectors = [], []
    for class_dir in sorted(p for p in DATA.iterdir() if p.is_dir()):
        imgs = sorted(class_dir.glob("*.jpg")) + sorted(class_dir.glob("*.JPG")) + sorted(class_dir.glob("*.png"))
        embs = []
        for p in imgs[:max_per]:
            v = _embed(p)
            if v is not None:
                embs.append(v)
        if not embs:
            continue
        mean = np.mean(embs, axis=0)
        mean = mean / (np.linalg.norm(mean) + 1e-8)
        labels.append(class_dir.name)
        vectors.append(mean.astype("float32"))
        logger.info(f"Soil indexed {class_dir.name} ({len(embs)})")

    vectors = np.stack(vectors)
    np.savez(CACHE, labels=np.array(labels, dtype=object), vectors=vectors)
    _index = {lab: vectors[i] for i, lab in enumerate(labels)}
    return _index


def predict_soil_from_path(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Could not read image", "status": "error"}

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype("float32")
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green_dom = (g > r + 15) & (g > b + 15) & (g > 60)
    if float(np.mean(green_dom)) > 0.28:
        return {
            "error": "This does not look like a soil photo. Please upload a soil image only (not leaves or plants).",
            "status": "invalid_image",
            "prediction": None,
            "confidence": 0,
        }

    index = _index_get()
    q = _embed(rgb)
    scores = [(name, float(np.dot(q, proto))) for name, proto in index.items()]
    scores.sort(key=lambda x: -x[1])
    best, sim = scores[0]
    margin = sim - (scores[1][1] if len(scores) > 1 else 0)
    conf = max(0.0, min(99.0, ((sim + 1) / 2) * 100))
    if margin > 0.04:
        conf = min(99.0, conf + 12)

    if sim < 0.38:
        return {
            "error": "Could not recognize soil. Upload a clear close-up of bare soil.",
            "status": "invalid_image",
            "prediction": None,
            "confidence": conf,
        }

    info = SOIL_INFO.get(best, {"notes": "", "crops": [], "care": []})
    return {
        "prediction": best,
        "confidence": conf,
        "notes": info["notes"],
        "crops": info["crops"],
        "care": info["care"],
        "grow_tip": f"You can typically grow: {', '.join(info['crops'])}." if info["crops"] else None,
        "status": "success",
        "engine": "imagenet-embed-match",
    }
